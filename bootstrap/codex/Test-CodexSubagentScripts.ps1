[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

function Write-Utf8NoBom {
    param([string]$Path, [string]$Content)

    $encoding = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Path, $Content, $encoding)
}

function Get-NonAgentSemanticHash {
    param([string]$Path)

    $result = & python $script:PythonHelperPath 'hash' $Path
    if ($LASTEXITCODE -ne 0) {
        throw 'Python TOML validation failed.'
    }
    return $result
}

function Assert-Toml {
    param([string]$Path, [string]$Check)

    & python $script:PythonHelperPath $Check $Path
    if ($LASTEXITCODE -ne 0) {
        throw "TOML assertion failed: $Check"
    }
}

$originalProfile = $env:USERPROFILE
$tempBase = [System.IO.Path]::GetFullPath($env:TEMP)
$tempRoot = Join-Path $tempBase ("task-0014-" + [guid]::NewGuid().ToString('N'))
$setScript = Join-Path $PSScriptRoot 'Set-CodexSubagentMode.ps1'
$statusScript = Join-Path $PSScriptRoot 'Get-CodexSubagentStatus.ps1'
$installScript = Join-Path $PSScriptRoot 'Install-CodexSubagents.ps1'

try {
    $codexDirectory = Join-Path $tempRoot '.codex'
    New-Item -ItemType Directory -Path $codexDirectory -Force | Out-Null
    $env:USERPROFILE = $tempRoot
    $configPath = Join-Path $codexDirectory 'config.toml'
    $script:PythonHelperPath = Join-Path $tempRoot 'validate_toml.py'
    Write-Utf8NoBom -Path $script:PythonHelperPath -Content @'
import hashlib
import json
import pathlib
import sys
import tomllib

check, file_name = sys.argv[1:3]
data = tomllib.loads(pathlib.Path(file_name).read_text(encoding="utf-8"))

if check == "hash":
    data.pop("agents", None)
    payload = json.dumps(data, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()
    print(hashlib.sha256(payload).hexdigest())
elif check == "manual_legacy":
    agents = data["agents"]
    assert agents["enabled"] is True
    assert agents["max_concurrent_threads_per_session"] == 4
    assert agents["max_threads"] == 4
    assert agents["custom_flag"] == "keep"
elif check == "off":
    agents = data["agents"]
    assert agents["enabled"] is False
    assert agents["max_concurrent_threads_per_session"] == 4
elif check == "readonly":
    assert data["sandbox_mode"] == "read-only"
    assert data["mcp_servers"]["feishu-docs"]["enabled"] is False
    assert data["mcp_servers"]["node_repl"]["enabled"] is False
else:
    raise ValueError(check)
'@

    Write-Utf8NoBom -Path $configPath -Content "model = `"gpt-test`"`n[agents]`nmax_threads = 9`ncustom_flag = `"keep`"`n[mcp_servers.demo]`ncommand = `"demo`"`n"
    $legacyStatus = & $statusScript
    if ($legacyStatus -notcontains 'Concurrent limit: 9') {
        throw 'Status did not read the legacy max_threads alias.'
    }
    $before = Get-NonAgentSemanticHash -Path $configPath
    $manualOutput = @(& $setScript -Mode Manual)
    if (($manualOutput -join "`n") -notmatch 'MANUAL is forbidden with --yolo') {
        throw 'MANUAL did not emit the live-permission safety prerequisite.'
    }
    $after = Get-NonAgentSemanticHash -Path $configPath
    if ($before -ne $after) {
        throw 'Non-agent configuration changed.'
    }
    Assert-Toml -Path $configPath -Check 'manual_legacy'
    if ((Get-ChildItem -LiteralPath $codexDirectory -Filter 'config.toml.bak.*').Count -ne 1) {
        throw 'Timestamped config backup was not created.'
    }
    'legacy-alias-preservation-and-manual-warning: PASS'

    Write-Utf8NoBom -Path $configPath -Content "[ `"agents`" ]`n`"enabled`" = true`n`"max_concurrent_threads_per_session`" = 7`n"
    & $setScript -Mode Off | Out-Null
    Assert-Toml -Path $configPath -Check 'off'
    'quoted-and-spaced-table: PASS'

    $lockedHashBefore = (Get-FileHash -Algorithm SHA256 -LiteralPath $configPath).Hash
    $lock = [System.IO.File]::Open($configPath, [System.IO.FileMode]::Open, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
    $lockRejected = $false
    try {
        try {
            & $setScript -Mode Manual | Out-Null
        }
        catch {
            $lockRejected = $true
        }
    }
    finally {
        $lock.Dispose()
    }
    $lockedHashAfter = (Get-FileHash -Algorithm SHA256 -LiteralPath $configPath).Hash
    if (-not $lockRejected -or $lockedHashBefore -ne $lockedHashAfter) {
        throw 'Concurrent config access did not fail closed.'
    }
    'concurrent-writer-lock: PASS'

    $tripleDoubleQuote = '"' * 3
    $tripleSingleQuote = "'" * 3
    $unsupportedFixtures = @(
        "agents.enabled = true`n",
        "agents = { enabled = true }`n",
        "[[agents]]`nname = `"unsupported`"`n",
        "text = $tripleDoubleQuote`n[agents]`nenabled = true`n$tripleDoubleQuote`n",
        "text = $tripleSingleQuote`n[agents]`nenabled = true`n$tripleSingleQuote`n"
    )
    foreach ($fixture in $unsupportedFixtures) {
        Write-Utf8NoBom -Path $configPath -Content $fixture
        $unsupportedStatus = & $statusScript
        if ($unsupportedStatus -notcontains 'Current mode: UNKNOWN (unsupported agents config shape)') {
            throw 'Status did not identify an unsupported agents configuration shape.'
        }
        $hashBefore = (Get-FileHash -Algorithm SHA256 -LiteralPath $configPath).Hash
        $failedClosed = $false
        try {
            & $setScript -Mode Off | Out-Null
        }
        catch {
            $failedClosed = $true
        }
        $hashAfter = (Get-FileHash -Algorithm SHA256 -LiteralPath $configPath).Hash
        if (-not $failedClosed -or $hashBefore -ne $hashAfter) {
            throw 'Unsupported TOML shape did not fail closed.'
        }
    }
    'unsupported-shapes-and-multiline-fail-closed: PASS'

    $agentDirectory = Join-Path $codexDirectory 'agents'
    New-Item -ItemType Directory -Path $agentDirectory -Force | Out-Null
    $existingTemplate = Join-Path $agentDirectory 'repo-explorer.toml'
    $existingContent = "name = `"custom_existing`"`n"
    $installFailureFixtures = @(
        @{ Name = 'inline'; Content = "agents = { enabled = true }`n"; Lock = $false },
        @{ Name = 'multiline'; Content = "text = $tripleDoubleQuote`n[agents]`nenabled = true`n$tripleDoubleQuote`n"; Lock = $false },
        @{ Name = 'locked'; Content = "[agents]`nenabled = true`nmax_concurrent_threads_per_session = 4`n"; Lock = $true }
    )
    foreach ($fixture in $installFailureFixtures) {
        Get-ChildItem -LiteralPath $agentDirectory -File -Filter '*.toml' | Remove-Item -Force
        Write-Utf8NoBom -Path $existingTemplate -Content $existingContent
        Write-Utf8NoBom -Path $configPath -Content $fixture.Content
        $configHashBefore = (Get-FileHash -Algorithm SHA256 -LiteralPath $configPath).Hash
        $templateHashBefore = (Get-FileHash -Algorithm SHA256 -LiteralPath $existingTemplate).Hash
        $lock = $null
        if ($fixture.Lock) {
            $lock = [System.IO.File]::Open($configPath, [System.IO.FileMode]::Open, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
        }
        $installFailed = $false
        $installOutput = @()
        try {
            try {
                $installOutput = @(& $installScript 2>&1)
            }
            catch {
                $installFailed = $true
                $installOutput += $_.Exception.Message
            }
        }
        finally {
            if ($null -ne $lock) {
                $lock.Dispose()
            }
        }
        if (-not $installFailed) {
            throw "Installation unexpectedly succeeded for $($fixture.Name)."
        }
        if ((Get-FileHash -Algorithm SHA256 -LiteralPath $configPath).Hash -ne $configHashBefore) {
            throw "Installation changed config.toml after OFF failure for $($fixture.Name)."
        }
        if ((Get-FileHash -Algorithm SHA256 -LiteralPath $existingTemplate).Hash -ne $templateHashBefore) {
            throw "Installation replaced an existing template after OFF failure for $($fixture.Name)."
        }
        $unexpectedTemplates = Get-ChildItem -LiteralPath $agentDirectory -File -Filter '*.toml' | Where-Object { $_.Name -ne 'repo-explorer.toml' }
        if (@($unexpectedTemplates).Count -ne 0) {
            throw "Installation added templates after OFF failure for $($fixture.Name)."
        }
        if (($installOutput -join "`n") -match 'Installation default: OFF') {
            throw "Installation emitted a false success message for $($fixture.Name)."
        }
    }
    'install-off-failure-atomicity: PASS'

    Write-Utf8NoBom -Path $configPath -Content ''
    Write-Utf8NoBom -Path $existingTemplate -Content $existingContent
    & $installScript | Out-Null
    $backups = Get-ChildItem -LiteralPath (Join-Path $agentDirectory '.backup') -Recurse -File -Filter 'repo-explorer.toml.bak'
    if ($backups.Count -ne 1) {
        throw 'Replaced Agent template was not backed up.'
    }
    Assert-Toml -Path $configPath -Check 'off'
    Get-ChildItem -LiteralPath $agentDirectory -File -Filter '*.toml' | ForEach-Object {
        Assert-Toml -Path $_.FullName -Check 'readonly'
    }
    'collision-backup-and-install-off: PASS'

    & $statusScript | Out-Null
    'status-runtime: PASS'
}
finally {
    $env:USERPROFILE = $originalProfile
    $resolvedTemp = [System.IO.Path]::GetFullPath($tempRoot)
    if (
        $resolvedTemp.StartsWith($tempBase, [System.StringComparison]::OrdinalIgnoreCase) -and
        (Test-Path -LiteralPath $resolvedTemp)
    ) {
        Remove-Item -LiteralPath $resolvedTemp -Recurse -Force
    }
}
