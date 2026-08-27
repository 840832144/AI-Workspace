[CmdletBinding()]
param(
    [string]$Root,
    [string]$StateDir,
    [string]$ProviderSnapshot
)

$workspaceRoot = if ($Root) { $Root } else { Split-Path -Parent (Split-Path -Parent $PSScriptRoot) }
$arguments = @('--root', $workspaceRoot)
if ($StateDir) { $arguments += @('--state-dir', $StateDir) }
$arguments += 'status'
if ($ProviderSnapshot) { $arguments += @('--provider-snapshot', $ProviderSnapshot) }
& (Join-Path $PSScriptRoot 'Invoke-WorkspaceContextCli.ps1') -CliArguments $arguments
exit $LASTEXITCODE
