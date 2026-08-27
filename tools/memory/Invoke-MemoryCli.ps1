[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$CliArguments
)

$ErrorActionPreference = 'Stop'
$cliPath = Join-Path $PSScriptRoot 'memory_cli.py'
$pythonCommand = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCommand) {
    $pythonCommand = Get-Command py -ErrorAction SilentlyContinue
}
if (-not $pythonCommand) {
    throw 'Python 3 is required. Install Python 3, then rerun this command.'
}

if ($pythonCommand.Name -eq 'py.exe' -or $pythonCommand.Name -eq 'py') {
    & $pythonCommand.Source -3 $cliPath @CliArguments
} else {
    & $pythonCommand.Source $cliPath @CliArguments
}
exit $LASTEXITCODE
