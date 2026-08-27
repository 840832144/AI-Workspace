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
$commandArguments = @($globalArguments + $refreshArguments)
& (Join-Path $PSScriptRoot 'Invoke-MemoryCli.ps1') -CliArguments $commandArguments
exit $LASTEXITCODE
