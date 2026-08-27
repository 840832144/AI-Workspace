[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$Path,
    [string]$Root,
    [string]$StateDir,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$CliArguments
)
$globalArguments = @()
if ($Root) { $globalArguments += @('--root', $Root) }
if ($StateDir) { $globalArguments += @('--state-dir', $StateDir) }
$commandArguments = @($globalArguments + @('validate', $Path))
if ($CliArguments) { $commandArguments += $CliArguments }
& (Join-Path $PSScriptRoot 'Invoke-MemoryCli.ps1') -CliArguments $commandArguments
exit $LASTEXITCODE
