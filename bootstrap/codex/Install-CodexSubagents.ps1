[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

$templateDirectory = Join-Path $PSScriptRoot 'agents'
$targetDirectory = Join-Path $env:USERPROFILE '.codex\agents'
$requiredTemplates = @(
    'repo-explorer.toml',
    'knowledge-retriever.toml',
    'evidence-test-verifier.toml',
    'reviewer.toml'
)

if (-not (Test-Path -LiteralPath $targetDirectory)) {
    New-Item -ItemType Directory -Path $targetDirectory -Force | Out-Null
}

$installed = [System.Collections.Generic.List[string]]::new()
$backupDirectory = $null
foreach ($fileName in $requiredTemplates) {
    $source = Join-Path $templateDirectory $fileName
    $target = Join-Path $targetDirectory $fileName
    if (-not (Test-Path -LiteralPath $source)) {
        throw "Missing versioned Agent template: $source"
    }

    $needsCopy = $true
    if (Test-Path -LiteralPath $target) {
        $sourceHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $source).Hash
        $targetHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $target).Hash
        $needsCopy = $sourceHash -ne $targetHash
    }

    if ($needsCopy) {
        if (Test-Path -LiteralPath $target) {
            if ($null -eq $backupDirectory) {
                $stamp = Get-Date -Format 'yyyyMMdd-HHmmss-fff'
                $backupDirectory = Join-Path $targetDirectory ".backup\$stamp"
                New-Item -ItemType Directory -Path $backupDirectory -Force | Out-Null
            }
            Copy-Item -LiteralPath $target -Destination (Join-Path $backupDirectory "$fileName.bak")
        }
        Copy-Item -LiteralPath $source -Destination $target -Force
    }
    $installed.Add($fileName)
}

& (Join-Path $PSScriptRoot 'Set-CodexSubagentMode.ps1') -Mode Off
"Installed templates: $($installed -join ', ')"
"Agent directory: $targetDirectory"
if ($null -ne $backupDirectory) {
    "Replaced-template backup: $backupDirectory"
}
'Installation default: OFF'
