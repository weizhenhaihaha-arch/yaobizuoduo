param(
    [Parameter(Mandatory = $true)]
    [string]$TaskId
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$statePath = Join-Path $projectRoot '.ag_loop_state.json'
$baselineCommit = (& git -C $projectRoot rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0) {
    throw 'Unable to record task baseline because git rev-parse failed.'
}
$recordedAt = Get-Date -Format 'yyyy-MM-dd HH:mm:ss K'
$state = [ordered]@{
    task_id = $TaskId
    baseline_commit = $baselineCommit
    recorded_at = $recordedAt
    last_progress_signature = ''
    last_progress_at = $recordedAt
    no_progress_checks = 0
    last_check_at = ''
}
$temporaryPath = "$statePath.tmp"
[System.IO.File]::WriteAllText($temporaryPath, ($state | ConvertTo-Json) + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
Move-Item -LiteralPath $temporaryPath -Destination $statePath -Force
Write-Output "Task baseline recorded: task=$TaskId commit=$baselineCommit"
