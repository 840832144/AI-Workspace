[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$CliArguments
)

$ErrorActionPreference = 'Stop'
$workspaceRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$cliPath = Join-Path $workspaceRoot 'tools\context\workspace_context.py'
$pythonCommand = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCommand) {
    $pythonCommand = Get-Command py -ErrorAction SilentlyContinue
}
if (-not $pythonCommand) {
    $bundledPython = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
    if (Test-Path -LiteralPath $bundledPython) {
        $pythonCommand = [pscustomobject]@{ Name = 'python.exe'; Source = $bundledPython }
    }
}
if (-not $pythonCommand) {
    throw 'Python 3 is required. Ask the workspace administrator to install the approved runtime.'
}

if ($pythonCommand.Name -in @('py.exe', 'py')) {
    & $pythonCommand.Source -3 $cliPath @CliArguments
} else {
    & $pythonCommand.Source $cliPath @CliArguments
}
exit $LASTEXITCODE
