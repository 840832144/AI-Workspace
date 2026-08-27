[CmdletBinding()]
param([string]$Root)

$ErrorActionPreference = 'Stop'
$workspaceRoot = if ($Root) { $Root } else { Split-Path -Parent (Split-Path -Parent $PSScriptRoot) }
$testPath = Join-Path $workspaceRoot 'tools\context\tests'
$pythonCommand = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCommand) { $pythonCommand = Get-Command py -ErrorAction SilentlyContinue }
if (-not $pythonCommand) {
    $bundledPython = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
    if (Test-Path -LiteralPath $bundledPython) { $pythonCommand = [pscustomobject]@{ Name = 'python.exe'; Source = $bundledPython } }
}
if (-not $pythonCommand) { throw 'Python 3 is required.' }

if ($pythonCommand.Name -in @('py.exe', 'py')) {
    & $pythonCommand.Source -3 -m unittest discover -s $testPath -v
} else {
    & $pythonCommand.Source -m unittest discover -s $testPath -v
}
exit $LASTEXITCODE
