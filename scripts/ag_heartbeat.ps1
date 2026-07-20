param(
    [int]$IntervalSeconds = 180,
    [switch]$Once
)

$projectRoot = Split-Path -Parent $PSScriptRoot
$statusPath = Join-Path $projectRoot 'AG_STATUS.md'
$historyPath = Join-Path $projectRoot 'AG_HEARTBEAT.log'
$reviewPath = Join-Path $projectRoot 'AG_REVIEW_REQUIRED.md'
$loopStatePath = Join-Path $projectRoot '.ag_loop_state.json'

function Write-Heartbeat {
    $checkedAt = Get-Date -Format 'yyyy-MM-dd HH:mm:ss K'
    $taskPath = Join-Path $projectRoot 'CURRENT_TASK.md'
    $taskText = if (Test-Path -LiteralPath $taskPath) { Get-Content -Raw -LiteralPath $taskPath } else { '' }
    $taskId = if ($taskText -match 'Task ID:\s*`([^`]+)`') { $Matches[1] } else { 'unknown' }
    $taskStatus = if ($taskText -match 'Status:\s*([^\r\n]+)') { $Matches[1].Trim() } else { 'unknown' }
    $branchState = (& git -C $projectRoot status --short --branch | Out-String).Trim()
    $latestCommit = (& git -C $projectRoot log -1 --pretty=format:'%h %s').Trim()
    $latestCommitHash = (& git -C $projectRoot rev-parse HEAD).Trim()
    $workingTree = if ($branchState -match '(?m)^## [^\r\n]+$') { 'clean' } else { 'changed' }
    $loopState = if (Test-Path -LiteralPath $loopStatePath) { Get-Content -Raw -LiteralPath $loopStatePath | ConvertFrom-Json } else { $null }
    $baselineCommit = if ($loopState) { [string]$loopState.baseline_commit } else { '' }
    $reviewRequired = -not [string]::IsNullOrWhiteSpace($baselineCommit) -and $latestCommitHash -ne $baselineCommit -and $taskStatus -match '^(dispatched|in_progress|repair_requested)$'

    $status = @(
        '# AG Heartbeat Status',
        '',
        "- Last check: $checkedAt",
        '- Check interval: 3 minutes',
        "- Current task: $taskId",
        "- Task status: $taskStatus",
        "- Working tree: $workingTree",
        "- Latest commit: $latestCommit",
        "- Dispatch baseline: $baselineCommit",
        "- Review required: $($reviewRequired.ToString().ToLowerInvariant())",
        '- Evidence scope: repository task files, Git state, and local validation results',
        '- Chat updates: unavailable while the conversation is closed',
        '',
        '## Git State',
        '',
        '```text',
        $branchState,
        '```'
    )
    [System.IO.File]::WriteAllText($statusPath, ($status -join [Environment]::NewLine) + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
    if ($reviewRequired) {
        $reviewNotice = "# AG Review Required`n`n- Detected: $checkedAt`n- Task: $taskId`n- Baseline: $baselineCommit`n- Current: $latestCommitHash`n- Action: main AG must review before dispatching another task.`n"
        [System.IO.File]::WriteAllText($reviewPath, $reviewNotice, [System.Text.UTF8Encoding]::new($false))
    } elseif (Test-Path -LiteralPath $reviewPath) {
        Remove-Item -LiteralPath $reviewPath -Force
    }
    Add-Content -LiteralPath $historyPath -Value "$checkedAt | task=$taskId | status=$taskStatus | tree=$workingTree | review=$reviewRequired | commit=$latestCommit"
}

do {
    Write-Heartbeat
    if (-not $Once) {
        Start-Sleep -Seconds $IntervalSeconds
    }
} while (-not $Once)
