[CmdletBinding()]
param(
    [string]$Root
)

$ErrorActionPreference = 'Stop'
if (-not $Root) {
    $Root = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
}
$python = Get-Command python -ErrorAction Stop
$cli = Join-Path $Root 'tools\tasks\task_cli.py'
$tests = Join-Path $Root 'tools\tasks\tests'

if (-not (Test-Path -LiteralPath $cli -PathType Leaf)) {
    throw "Task CLI not found: $cli"
}

& $python.Source -m py_compile $cli
if ($LASTEXITCODE -ne 0) { throw 'task_cli.py compile failed' }
'python-compile: PASS'

& $python.Source -m unittest discover -s $tests -v
if ($LASTEXITCODE -ne 0) { throw 'disposable Task allocator tests failed' }
'disposable-fixtures: PASS'

$scanOutput = & $python.Source $cli --root $Root scan
if ($LASTEXITCODE -ne 0) { throw "real repository scan failed: $scanOutput" }
$scan = $scanOutput | ConvertFrom-Json
if ($scan.collision_count -ne 0) { throw 'real repository has canonical Task collisions' }
if ($scan.canonical_count -lt 8) { throw "unexpected canonical Task count: $($scan.canonical_count)" }
"real-repository-scan: PASS ($($scan.canonical_count) canonical, 0 collisions)"

$validateOutput = & $python.Source $cli --root $Root validate
if ($LASTEXITCODE -ne 0) { throw "real repository validation failed: $validateOutput" }
'real-repository-validate: PASS'

$lottery = Join-Path $Root 'tasks\TASK-0018-Huuuge-Lottery-Numerical-Breakdown-Report.md'
$stub = Join-Path $Root 'tasks\TASK-0018-Cash-Frenzy-Android-Collector-Feasibility-Audit.md'
$candidate = Join-Path $Root 'tasks\candidates\CANDIDATE-20260827-CASH-FRENZY-COLLECTOR-FEASIBILITY.md'
if (-not (Test-Path -LiteralPath $lottery -PathType Leaf)) { throw 'canonical Huuuge TASK-0018 is missing' }
if (-not (Select-String -LiteralPath $stub -SimpleMatch '- Kind: companion' -Quiet)) { throw 'Cash Frenzy collision stub is not companion' }
if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) { throw 'Cash Frenzy Candidate is missing' }
if (-not (Select-String -LiteralPath $candidate -SimpleMatch '## Non-execution Notice' -Quiet)) { throw 'Cash Frenzy Candidate provenance notice is missing' }
'incident-repair: PASS (Lottery canonical; Cash Frenzy Candidate non-executable)'

'Task Registry validation: PASS'
