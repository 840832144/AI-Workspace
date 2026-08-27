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
& (Join-Path $PSScriptRoot 'Invoke-MemoryCli.ps1') @globalArguments validate $Path @CliArguments
exit $LASTEXITCODE
