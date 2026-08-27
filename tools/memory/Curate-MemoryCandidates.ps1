[CmdletBinding()]
param(
    [string]$Root,
    [string]$StateDir,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$CliArguments
)
$globalArguments = @()
if ($Root) { $globalArguments += @('--root', $Root) }
if ($StateDir) { $globalArguments += @('--state-dir', $StateDir) }
& (Join-Path $PSScriptRoot 'Invoke-MemoryCli.ps1') @globalArguments curate @CliArguments
exit $LASTEXITCODE
