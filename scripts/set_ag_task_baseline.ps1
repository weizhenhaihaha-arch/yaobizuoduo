param(
    [Parameter(Mandatory = $true)]
    [string]$TaskId
)

$projectRoot = Split-Path -Parent $PSScriptRoot
$statePath = Join-Path $projectRoot '.ag_loop_state.json'
$baselineCommit = (& git -C $projectRoot rev-parse HEAD).Trim()
$state = [ordered]@{
    task_id = $TaskId
    baseline_commit = $baselineCommit
    recorded_at = (Get-Date -Format 'yyyy-MM-dd HH:mm:ss K')
}
[System.IO.File]::WriteAllText($statePath, ($state | ConvertTo-Json) + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
Write-Output "Task baseline recorded: task=$TaskId commit=$baselineCommit"
