param(
    [int]$IntervalSeconds = 180,
    [switch]$Once
)

$projectRoot = Split-Path -Parent $PSScriptRoot
$statusPath = Join-Path $projectRoot 'AG_STATUS.md'
$historyPath = Join-Path $projectRoot 'AG_HEARTBEAT.log'

function Write-Heartbeat {
    $checkedAt = Get-Date -Format 'yyyy-MM-dd HH:mm:ss K'
    $taskPath = Join-Path $projectRoot 'CURRENT_TASK.md'
    $taskText = if (Test-Path -LiteralPath $taskPath) { Get-Content -Raw -LiteralPath $taskPath } else { '' }
    $taskId = if ($taskText -match 'Task ID:\s*`([^`]+)`') { $Matches[1] } else { 'unknown' }
    $taskStatus = if ($taskText -match 'Status:\s*([^\r\n]+)') { $Matches[1].Trim() } else { 'unknown' }
    $branchState = (& git -C $projectRoot status --short --branch | Out-String).Trim()
    $latestCommit = (& git -C $projectRoot log -1 --pretty=format:'%h %s').Trim()
    $workingTree = if ($branchState -match '(?m)^## [^\r\n]+$') { 'clean' } else { 'changed' }

    $status = @(
        '# AG Heartbeat Status',
        '',
        "- Last check: $checkedAt",
        '- Check interval: 3 minutes',
        "- Current task: $taskId",
        "- Task status: $taskStatus",
        "- Working tree: $workingTree",
        "- Latest commit: $latestCommit",
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
    Add-Content -LiteralPath $historyPath -Value "$checkedAt | task=$taskId | status=$taskStatus | tree=$workingTree | commit=$latestCommit"
}

do {
    Write-Heartbeat
    if (-not $Once) {
        Start-Sleep -Seconds $IntervalSeconds
    }
} while (-not $Once)
