param([switch]$Force)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$lockPath = Join-Path $projectRoot '.ag_supervisor.lock'
if ((Test-Path -LiteralPath $lockPath) -and -not $Force) {
    throw 'Supervisor lock exists. Verify no supervisor process is running, then retry with -Force.'
}
foreach ($name in @('.ag_supervisor_state.json', '.ag_supervisor.lock', 'AG_SUPERVISOR_ERROR.md', 'AG_SUPERVISOR_BLOCKED.md')) {
    $path = Join-Path $projectRoot $name
    if (Test-Path -LiteralPath $path) {
        Remove-Item -LiteralPath $path -Force
    }
}
Write-Output 'Autonomous supervisor failure state reset.'
