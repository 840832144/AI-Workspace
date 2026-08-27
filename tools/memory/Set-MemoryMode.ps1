[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('Off', 'Assisted', 'Auto')]
    [string]$Mode,
    [string]$Root,
    [string]$StateDir,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$CliArguments
)
$globalArguments = @()
if ($Root) { $globalArguments += @('--root', $Root) }
if ($StateDir) { $globalArguments += @('--state-dir', $StateDir) }
$commandArguments = @($globalArguments + @('set-mode', $Mode))
if ($CliArguments) { $commandArguments += $CliArguments }
& (Join-Path $PSScriptRoot 'Invoke-MemoryCli.ps1') -CliArguments $commandArguments
exit $LASTEXITCODE
