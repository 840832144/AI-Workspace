[CmdletBinding()]
param(
    [string]$Root,
    [string]$StateDir,
    [switch]$Sync,
    [switch]$IncludeRegisteredRepositories
)
$globalArguments = @()
if ($Root) { $globalArguments += @('--root', $Root) }
if ($StateDir) { $globalArguments += @('--state-dir', $StateDir) }
$refreshArguments = @('refresh')
if ($Sync) { $refreshArguments += '--sync' }
if ($IncludeRegisteredRepositories) { $refreshArguments += '--include-registered-repositories' }
& (Join-Path $PSScriptRoot 'Invoke-MemoryCli.ps1') @globalArguments @refreshArguments
exit $LASTEXITCODE
