param(
    [switch]$Once,
    [switch]$DryRun,
    [int]$MaxRunMinutes = 45,
    [int]$MaxFailures = 3
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$lockPath = Join-Path $projectRoot '.ag_supervisor.lock'
$statePath = Join-Path $projectRoot '.ag_supervisor_state.json'
$statusPath = Join-Path $projectRoot 'AG_SUPERVISOR_STATUS.md'
$lastMessagePath = Join-Path $projectRoot 'AG_SUPERVISOR_LAST.md'
$errorPath = Join-Path $projectRoot 'AG_SUPERVISOR_ERROR.md'
$blockedPath = Join-Path $projectRoot 'AG_SUPERVISOR_BLOCKED.md'
$logPath = Join-Path $projectRoot 'AG_SUPERVISOR.log'
$loopStatePath = Join-Path $projectRoot '.ag_loop_state.json'
$heartbeatStatusPath = Join-Path $projectRoot 'AG_STATUS.md'
$basePromptPath = Join-Path $projectRoot 'automation\SUPERVISOR_BASE.md'
$reviewPromptPath = Join-Path $projectRoot 'automation\REVIEW_PROMPT.md'
$workPromptPath = Join-Path $projectRoot 'automation\WORK_PROMPT.md'
$outputSchemaPath = Join-Path $projectRoot 'automation\supervisor_output.schema.json'
$codexPath = (Get-Command codex.exe -ErrorAction Stop).Source
$activeStatuses = @('dispatched', 'in_progress', 'repair_requested', 'awaiting_review')
$lockStream = $null

function Write-Utf8Atomic {
    param([string]$Path, [string]$Content)
    $temporaryPath = "$Path.tmp"
    [System.IO.File]::WriteAllText($temporaryPath, $Content, [System.Text.UTF8Encoding]::new($false))
    Move-Item -LiteralPath $temporaryPath -Destination $Path -Force
}

function Quote-ProcessArgument {
    param([string]$Value)
    return '"' + ($Value -replace '"', '\"') + '"'
}

function Get-GitOutput {
    param([string[]]$Arguments)
    $output = (& git -C $projectRoot @Arguments 2>&1 | Out-String).Trim()
    if ($LASTEXITCODE -ne 0) {
        throw "git $($Arguments -join ' ') failed: $output"
    }
    return $output
}

function Read-JsonState {
    if (-not (Test-Path -LiteralPath $statePath)) {
        return [pscustomobject]@{ consecutive_failures = 0; next_retry_at = ''; blocked = $false }
    }
    return Get-Content -Raw -LiteralPath $statePath | ConvertFrom-Json
}

function Write-SupervisorState {
    param([int]$Failures, [string]$NextRetryAt, [bool]$Blocked, [string]$LastAction, [string]$LastResult)
    $state = [ordered]@{
        consecutive_failures = $Failures
        next_retry_at = $NextRetryAt
        blocked = $Blocked
        last_action = $LastAction
        last_result = $LastResult
        last_run_at = (Get-Date -Format 'yyyy-MM-dd HH:mm:ss K')
    }
    Write-Utf8Atomic -Path $statePath -Content (($state | ConvertTo-Json) + [Environment]::NewLine)
}

function Write-SupervisorStatus {
    param([string]$Action, [string]$Result, [string]$TaskId, [string]$TaskStatus, [string]$Details)
    $content = @(
        '# AG Autonomous Supervisor Status',
        '',
        "- Last run: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss K')",
        '- Schedule: every 3 minutes',
        "- Task: $TaskId",
        "- Task status: $TaskStatus",
        "- Selected action: $Action",
        "- Result: $Result",
        "- Details: $Details",
        '- Runtime: Codex CLI non-interactive, danger-full-access fallback, approvals disabled',
        '- Safety: one transition, exclusive lock, structured output, Git/status postconditions, failure backoff, no Git push'
    )
    Write-Utf8Atomic -Path $statusPath -Content (($content -join [Environment]::NewLine) + [Environment]::NewLine)
}

function Add-SupervisorLog {
    param([string]$Message)
    if ((Test-Path -LiteralPath $logPath) -and (Get-Item -LiteralPath $logPath).Length -gt 2MB) {
        $tail = Get-Content -LiteralPath $logPath -Tail 1000
        Write-Utf8Atomic -Path $logPath -Content (($tail -join [Environment]::NewLine) + [Environment]::NewLine)
    }
    Add-Content -LiteralPath $logPath -Value "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss K') | $Message"
}

function Acquire-SupervisorLock {
    try {
        $script:lockStream = [System.IO.File]::Open($lockPath, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
    } catch [System.IO.IOException] {
        $existing = if (Test-Path -LiteralPath $lockPath) { Get-Content -Raw -LiteralPath $lockPath -ErrorAction SilentlyContinue } else { '' }
        Add-SupervisorLog -Message "skip=lock_held details=$existing"
        return $false
    }
    $lockContent = "pid=$PID`nstarted_at=$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss K')`n"
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($lockContent)
    $script:lockStream.Write($bytes, 0, $bytes.Length)
    $script:lockStream.Flush()
    return $true
}

function Release-SupervisorLock {
    if ($script:lockStream) {
        $script:lockStream.Dispose()
        $script:lockStream = $null
    }
    if (Test-Path -LiteralPath $lockPath) {
        Remove-Item -LiteralPath $lockPath -Force -ErrorAction SilentlyContinue
    }
}

function Invoke-CodexTransition {
    param([string]$Prompt)
    $arguments = @(
        '-a', 'never',
        '-s', 'danger-full-access',
        '-C', $projectRoot,
        'exec',
        '--ephemeral',
        '--color', 'never',
        '--output-schema', $outputSchemaPath,
        '--output-last-message', $lastMessagePath,
        '-'
    )
    $startInfo = [System.Diagnostics.ProcessStartInfo]::new()
    $startInfo.FileName = $codexPath
    $startInfo.Arguments = (($arguments | ForEach-Object { Quote-ProcessArgument $_ }) -join ' ')
    $startInfo.WorkingDirectory = $projectRoot
    $startInfo.UseShellExecute = $false
    $startInfo.CreateNoWindow = $true
    $startInfo.RedirectStandardInput = $true
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true
    $process = [System.Diagnostics.Process]::new()
    $process.StartInfo = $startInfo
    if (-not $process.Start()) {
        throw 'Unable to start codex supervisor process.'
    }
    $stdoutTask = $process.StandardOutput.ReadToEndAsync()
    $stderrTask = $process.StandardError.ReadToEndAsync()
    $process.StandardInput.Write($Prompt)
    $process.StandardInput.Close()
    if (-not $process.WaitForExit($MaxRunMinutes * 60 * 1000)) {
        $process.Kill()
        throw "Codex transition exceeded $MaxRunMinutes minutes."
    }
    $stdout = $stdoutTask.Result
    $stderr = $stderrTask.Result
    Add-SupervisorLog -Message "codex_exit=$($process.ExitCode) stdout=$($stdout -replace '[\r\n]+', ' ') stderr=$($stderr -replace '[\r\n]+', ' ')"
    if ($process.ExitCode -ne 0) {
        throw "Codex exited with code $($process.ExitCode): $stderr"
    }
    if (-not (Test-Path -LiteralPath $lastMessagePath)) {
        throw 'Codex produced no structured last-message file.'
    }
    try {
        $result = Get-Content -Raw -LiteralPath $lastMessagePath | ConvertFrom-Json
    } catch {
        throw "Codex last message is not valid supervisor JSON: $($_.Exception.Message)"
    }
    if ([string]$result.transition_status -ne 'completed') {
        throw "Codex reported transition_status=$($result.transition_status): $($result.summary)"
    }
    return $result
}

if (-not (Acquire-SupervisorLock)) {
    exit 0
}

try {
    $supervisorState = Read-JsonState
    if ([bool]$supervisorState.blocked) {
        Write-SupervisorStatus -Action 'none' -Result 'blocked' -TaskId 'unknown' -TaskStatus 'unknown' -Details 'Manual reset required after repeated failures.'
        exit 0
    }
    if ($supervisorState.next_retry_at) {
        $retryAt = [DateTimeOffset]::Parse([string]$supervisorState.next_retry_at)
        if ([DateTimeOffset]::Now -lt $retryAt) {
            Write-SupervisorStatus -Action 'none' -Result 'backoff' -TaskId 'unknown' -TaskStatus 'unknown' -Details "Next retry: $retryAt"
            exit 0
        }
    }
    if (Test-Path -LiteralPath (Join-Path $projectRoot 'AG_LOOP_ERROR.md')) {
        Write-SupervisorStatus -Action 'none' -Result 'heartbeat_error' -TaskId 'unknown' -TaskStatus 'unknown' -Details 'Repair AG_LOOP_ERROR.md before autonomous execution.'
        exit 0
    }

    $taskText = Get-Content -Raw -LiteralPath (Join-Path $projectRoot 'CURRENT_TASK.md')
    $taskId = if ($taskText -match 'Task ID:\s*`([^`]+)`') { $Matches[1] } else { 'unknown' }
    $taskStatus = if ($taskText -match 'Status:\s*([^\r\n]+)') { $Matches[1].Trim() } else { 'unknown' }
    $loopState = Get-Content -Raw -LiteralPath $loopStatePath | ConvertFrom-Json
    $head = Get-GitOutput -Arguments @('rev-parse', 'HEAD')
    $branchState = Get-GitOutput -Arguments @('status', '--short', '--branch')
    $treeChanged = $branchState -notmatch '(?m)^## [^\r\n]+$'
    $baselineMatchesTask = [string]$loopState.task_id -eq $taskId
    $headDiffersFromBaseline = $head -ne [string]$loopState.baseline_commit
    $reviewRequired = (Test-Path -LiteralPath (Join-Path $projectRoot 'AG_REVIEW_REQUIRED.md')) -or ($baselineMatchesTask -and $headDiffersFromBaseline -and $activeStatuses -contains $taskStatus)
    $wakeRequired = Test-Path -LiteralPath (Join-Path $projectRoot 'AG_WAKE_REQUIRED.md')

    $action = 'none'
    if (-not $baselineMatchesTask) {
        $action = 'none'
        Write-SupervisorStatus -Action $action -Result 'baseline_mismatch' -TaskId $taskId -TaskStatus $taskStatus -Details 'Run set_ag_task_baseline.ps1 before autonomous execution.'
        exit 0
    } elseif ($reviewRequired -or $taskStatus -eq 'awaiting_review') {
        $action = 'review'
    } elseif (($taskStatus -in @('dispatched', 'repair_requested')) -and (-not $treeChanged -or $wakeRequired)) {
        $action = 'work'
    } elseif ($wakeRequired -and $activeStatuses -contains $taskStatus) {
        $action = 'work'
    }

    if ($action -eq 'none') {
        Write-SupervisorState -Failures 0 -NextRetryAt '' -Blocked $false -LastAction 'none' -LastResult 'monitoring'
        Write-SupervisorStatus -Action 'none' -Result 'monitoring' -TaskId $taskId -TaskStatus $taskStatus -Details 'No safe transition is currently required.'
        Add-SupervisorLog -Message "task=$taskId status=$taskStatus action=none tree_changed=$treeChanged"
        exit 0
    }

    $promptFile = if ($action -eq 'review') { $reviewPromptPath } else { $workPromptPath }
    $prompt = (Get-Content -Raw -LiteralPath $basePromptPath) + "`n`n" + (Get-Content -Raw -LiteralPath $promptFile) + "`n`nRuntime action: $action`nRuntime task: $taskId`n"
    if ($DryRun) {
        Write-SupervisorStatus -Action $action -Result 'dry_run' -TaskId $taskId -TaskStatus $taskStatus -Details "Would invoke Codex using $promptFile"
        Add-SupervisorLog -Message "task=$taskId status=$taskStatus action=$action dry_run=true"
        exit 0
    }

    Write-SupervisorStatus -Action $action -Result 'running' -TaskId $taskId -TaskStatus $taskStatus -Details 'Codex transition is running under the exclusive supervisor lock.'
    Add-SupervisorLog -Message "task=$taskId status=$taskStatus action=$action start"
    $preTransitionHead = $head
    $transitionResult = Invoke-CodexTransition -Prompt $prompt
    $postTransitionHead = Get-GitOutput -Arguments @('rev-parse', 'HEAD')
    $postTaskText = Get-Content -Raw -LiteralPath (Join-Path $projectRoot 'CURRENT_TASK.md')
    $postTaskId = if ($postTaskText -match 'Task ID:\s*`([^`]+)`') { $Matches[1] } else { 'unknown' }
    $postTaskStatus = if ($postTaskText -match 'Status:\s*([^\r\n]+)') { $Matches[1].Trim() } else { 'unknown' }
    if ($postTransitionHead -eq $preTransitionHead) {
        throw 'Codex returned completed but created no repository commit.'
    }
    if ($action -eq 'work' -and $postTaskStatus -notin @('awaiting_review', 'blocked')) {
        throw "Work transition ended with invalid task status: $postTaskStatus"
    }
    if ($action -eq 'review' -and $postTaskStatus -notin @('dispatched', 'repair_requested', 'blocked')) {
        throw "Review transition ended with invalid task status: $postTaskStatus"
    }
    if ([string]$transitionResult.action -ne $action) {
        throw "Structured result action mismatch: expected $action, got $($transitionResult.action)"
    }
    powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $projectRoot 'scripts\ag_heartbeat.ps1') -Once | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw 'Heartbeat refresh failed after Codex transition.'
    }
    Write-SupervisorState -Failures 0 -NextRetryAt '' -Blocked $false -LastAction $action -LastResult 'success'
    Write-SupervisorStatus -Action $action -Result 'success' -TaskId $postTaskId -TaskStatus $postTaskStatus -Details "Commit $postTransitionHead completed one validated transition."
    if (Test-Path -LiteralPath $errorPath) { Remove-Item -LiteralPath $errorPath -Force }
    Add-SupervisorLog -Message "task=$taskId action=$action result=success"
} catch {
    $previousState = Read-JsonState
    $failures = [int]$previousState.consecutive_failures + 1
    $blocked = $failures -ge $MaxFailures
    $delayMinutes = [Math]::Min(60, 5 * [Math]::Pow(2, [Math]::Max(0, $failures - 1)))
    $nextRetry = if ($blocked) { '' } else { [DateTimeOffset]::Now.AddMinutes($delayMinutes).ToString('o') }
    Write-SupervisorState -Failures $failures -NextRetryAt $nextRetry -Blocked $blocked -LastAction 'error' -LastResult $_.Exception.Message
    Write-Utf8Atomic -Path $errorPath -Content "# AG Supervisor Error`n`n- Detected: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss K')`n- Failure count: $failures/$MaxFailures`n- Error: $($_.Exception.Message)`n- Next retry: $nextRetry`n"
    if ($blocked) {
        Write-Utf8Atomic -Path $blockedPath -Content "# AG Supervisor Blocked`n`n- Detected: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss K')`n- Reason: $failures consecutive supervisor failures`n- Action: main AG must inspect logs and reset `.ag_supervisor_state.json`.`n"
    }
    Write-SupervisorStatus -Action 'error' -Result $(if ($blocked) { 'blocked' } else { 'backoff' }) -TaskId 'unknown' -TaskStatus 'unknown' -Details $_.Exception.Message
    Add-SupervisorLog -Message "action=error failures=$failures blocked=$blocked error=$($_.Exception.Message)"
    throw
} finally {
    Release-SupervisorLock
}
