[CmdletBinding()]
param(
    [string]$Root,
    [string]$StateDir
)

$ErrorActionPreference = 'Stop'
$workspaceRoot = if ($Root) { $Root } else { Split-Path -Parent (Split-Path -Parent $PSScriptRoot) }
$arguments = @('--root', $workspaceRoot)
if ($StateDir) { $arguments += @('--state-dir', $StateDir) }
$arguments += @('set-mode', 'ON_DEMAND')
& (Join-Path $PSScriptRoot 'Invoke-WorkspaceContextCli.ps1') -CliArguments $arguments
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$doctor = @('--root', $workspaceRoot)
if ($StateDir) { $doctor += @('--state-dir', $StateDir) }
$doctor += 'doctor'
& (Join-Path $PSScriptRoot 'Invoke-WorkspaceContextCli.ps1') -CliArguments $doctor
exit $LASTEXITCODE
