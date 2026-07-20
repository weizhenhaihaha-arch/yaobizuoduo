param(
    [int]$IntervalSeconds = 180,
    [int]$WakeAfterChecks = 3,
    [switch]$Once
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$statusPath = Join-Path $projectRoot 'AG_STATUS.md'
$historyPath = Join-Path $projectRoot 'AG_HEARTBEAT.log'
$reviewPath = Join-Path $projectRoot 'AG_REVIEW_REQUIRED.md'
$wakePath = Join-Path $projectRoot 'AG_WAKE_REQUIRED.md'
$errorPath = Join-Path $projectRoot 'AG_LOOP_ERROR.md'
$loopStatePath = Join-Path $projectRoot '.ag_loop_state.json'
$activeStatuses = @('dispatched', 'in_progress', 'repair_requested')

function Write-Utf8Atomic {
    param([string]$Path, [string]$Content)
    $temporaryPath = "$Path.tmp"
    [System.IO.File]::WriteAllText($temporaryPath, $Content, [System.Text.UTF8Encoding]::new($false))
    Move-Item -LiteralPath $temporaryPath -Destination $Path -Force
}

function Get-GitOutput {
    param([string[]]$Arguments)
    $output = (& git -C $projectRoot @Arguments 2>&1 | Out-String).Trim()
    if ($LASTEXITCODE -ne 0) {
        throw "git $($Arguments -join ' ') failed: $output"
    }
    return $output
}

function Get-ProgressSignature {
    param([string]$CommitHash)
    $changedFileText = Get-GitOutput -Arguments @('ls-files', '--modified', '--others', '--exclude-standard')
    $changedFiles = @($changedFileText -split "`r?`n" | Where-Object { $_ })
    $parts = [System.Collections.Generic.List[string]]::new()
    $parts.Add($CommitHash)
    foreach ($relativePath in ($changedFiles | Sort-Object -Unique)) {
        $fullPath = Join-Path $projectRoot $relativePath
        if (Test-Path -LiteralPath $fullPath -PathType Leaf) {
            $item = Get-Item -LiteralPath $fullPath
            $parts.Add("$relativePath|$($item.Length)|$($item.LastWriteTimeUtc.Ticks)")
        } else {
            $parts.Add("$relativePath|missing")
        }
    }
    $bytes = [System.Text.Encoding]::UTF8.GetBytes(($parts -join "`n"))
    $sha256 = [System.Security.Cryptography.SHA256]::Create()
    try {
        $hash = $sha256.ComputeHash($bytes)
        return ([BitConverter]::ToString($hash) -replace '-', '').ToLowerInvariant()
    } finally {
        $sha256.Dispose()
    }
}

function Rotate-History {
    if ((Test-Path -LiteralPath $historyPath) -and (Get-Item -LiteralPath $historyPath).Length -gt 2MB) {
        $tail = Get-Content -LiteralPath $historyPath -Tail 1000
        Write-Utf8Atomic -Path $historyPath -Content (($tail -join [Environment]::NewLine) + [Environment]::NewLine)
    }
}

function Write-Heartbeat {
    $checkedAt = Get-Date
    $checkedAtText = $checkedAt.ToString('yyyy-MM-dd HH:mm:ss K')
    $taskPath = Join-Path $projectRoot 'CURRENT_TASK.md'
    $taskText = if (Test-Path -LiteralPath $taskPath) { Get-Content -Raw -LiteralPath $taskPath } else { '' }
    $taskId = if ($taskText -match 'Task ID:\s*`([^`]+)`') { $Matches[1] } else { 'unknown' }
    $taskStatus = if ($taskText -match 'Status:\s*([^\r\n]+)') { $Matches[1].Trim() } else { 'unknown' }
    $branchState = Get-GitOutput @('status', '--short', '--branch')
    $latestCommit = Get-GitOutput @('log', '-1', '--pretty=format:%h %s')
    $latestCommitHash = Get-GitOutput @('rev-parse', 'HEAD')
    $workingTree = if ($branchState -match '(?m)^## [^\r\n]+$') { 'clean' } else { 'changed' }
    $loopState = if (Test-Path -LiteralPath $loopStatePath) { Get-Content -Raw -LiteralPath $loopStatePath | ConvertFrom-Json } else { $null }
    $baselineCommit = if ($loopState) { [string]$loopState.baseline_commit } else { '' }
    $baselineTaskId = if ($loopState) { [string]$loopState.task_id } else { '' }
    $loopStateValid = -not [string]::IsNullOrWhiteSpace($baselineCommit) -and $baselineTaskId -eq $taskId
    $isActive = $activeStatuses -contains $taskStatus
    $reviewRequired = $loopStateValid -and $latestCommitHash -ne $baselineCommit -and $isActive
    $progressSignature = Get-ProgressSignature -CommitHash $latestCommitHash
    $previousSignature = if ($loopState -and $loopState.PSObject.Properties.Name -contains 'last_progress_signature') { [string]$loopState.last_progress_signature } else { '' }
    $progressDetected = $progressSignature -ne $previousSignature
    $lastProgressAt = if ($progressDetected -or -not $loopState -or -not ($loopState.PSObject.Properties.Name -contains 'last_progress_at')) { $checkedAtText } else { [string]$loopState.last_progress_at }
    $noProgressChecks = if ($progressDetected -or -not $isActive -or $reviewRequired) { 0 } elseif ($loopState -and $loopState.PSObject.Properties.Name -contains 'no_progress_checks') { [int]$loopState.no_progress_checks + 1 } else { 1 }
    $wakeRequired = $loopStateValid -and $isActive -and -not $reviewRequired -and $noProgressChecks -ge $WakeAfterChecks
    $nextAction = if (-not $loopStateValid) { 'reset_task_baseline' } elseif ($reviewRequired) { 'main_ag_review' } elseif ($wakeRequired) { 'main_ag_wake_or_status_request' } elseif ($isActive) { 'continue_monitoring' } else { 'main_ag_dispatch_or_close_task' }

    $state = [ordered]@{
        task_id = $baselineTaskId
        baseline_commit = $baselineCommit
        recorded_at = if ($loopState) { [string]$loopState.recorded_at } else { '' }
        last_progress_signature = $progressSignature
        last_progress_at = $lastProgressAt
        no_progress_checks = $noProgressChecks
        last_check_at = $checkedAtText
    }
    Write-Utf8Atomic -Path $loopStatePath -Content (($state | ConvertTo-Json) + [Environment]::NewLine)

    $status = @(
        '# AG Heartbeat Status',
        '',
        "- Last check: $checkedAtText",
        '- Check interval: 3 minutes',
        "- Current task: $taskId",
        "- Task status: $taskStatus",
        "- Working tree: $workingTree",
        "- Latest commit: $latestCommit",
        "- Dispatch baseline: $baselineCommit",
        "- Loop state valid: $($loopStateValid.ToString().ToLowerInvariant())",
        "- Progress detected: $($progressDetected.ToString().ToLowerInvariant())",
        "- Last progress: $lastProgressAt",
        "- Consecutive no-progress checks: $noProgressChecks/$WakeAfterChecks",
        "- Review required: $($reviewRequired.ToString().ToLowerInvariant())",
        "- Wake required: $($wakeRequired.ToString().ToLowerInvariant())",
        "- Next action: $nextAction",
        '- Evidence scope: repository task files, Git state, changed-file timestamps, and local validation results',
        '- Chat updates: unavailable while the conversation is closed',
        '',
        '## Git State',
        '',
        '```text',
        $branchState,
        '```'
    )
    Write-Utf8Atomic -Path $statusPath -Content (($status -join [Environment]::NewLine) + [Environment]::NewLine)

    if ($reviewRequired) {
        Write-Utf8Atomic -Path $reviewPath -Content "# AG Review Required`n`n- Detected: $checkedAtText`n- Task: $taskId`n- Baseline: $baselineCommit`n- Current: $latestCommitHash`n- Action: main AG must review before dispatching another task.`n"
    } elseif (Test-Path -LiteralPath $reviewPath) {
        Remove-Item -LiteralPath $reviewPath -Force
    }
    if ($wakeRequired) {
        Write-Utf8Atomic -Path $wakePath -Content "# AG Wake Required`n`n- Detected: $checkedAtText`n- Task: $taskId`n- Last progress: $lastProgressAt`n- No-progress checks: $noProgressChecks`n- Action: active main AG session must request executor status or wake the executor.`n"
    } elseif (Test-Path -LiteralPath $wakePath) {
        Remove-Item -LiteralPath $wakePath -Force
    }
    if (Test-Path -LiteralPath $errorPath) {
        Remove-Item -LiteralPath $errorPath -Force
    }
    Rotate-History
    Add-Content -LiteralPath $historyPath -Value "$checkedAtText | task=$taskId | status=$taskStatus | tree=$workingTree | progress=$progressDetected | idle=$noProgressChecks | review=$reviewRequired | wake=$wakeRequired | action=$nextAction | commit=$latestCommit"
}

do {
    try {
        Write-Heartbeat
    } catch {
        $failedAt = Get-Date -Format 'yyyy-MM-dd HH:mm:ss K'
        Write-Utf8Atomic -Path $errorPath -Content "# AG Loop Error`n`n- Detected: $failedAt`n- Error: $($_.Exception.Message)`n- Action: main AG must repair the heartbeat before claiming the loop is healthy.`n"
        throw
    }
    if (-not $Once) {
        Start-Sleep -Seconds $IntervalSeconds
    }
} while (-not $Once)
