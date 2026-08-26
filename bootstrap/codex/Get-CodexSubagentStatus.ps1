[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

$configPath = Join-Path $env:USERPROFILE '.codex\config.toml'
$agentDirectory = Join-Path $env:USERPROFILE '.codex\agents'
$enabled = $null
$limit = $null

if (Test-Path -LiteralPath $configPath) {
    $text = [System.IO.File]::ReadAllText($configPath)
    $tripleDoubleQuote = '"' * 3
    $tripleSingleQuote = "'" * 3
    $section = [regex]::Match(
        $text,
        '(?ms)^[ \t]*\[[ \t]*(?:"agents"|''agents''|agents)[ \t]*\][ \t]*(?:#.*)?\r?\n(?<body>.*?)(?=^[ \t]*\[\[?.+\]\]?[ \t]*(?:#.*)?$|\z)'
    )
    if ($section.Success) {
        $enabledMatch = [regex]::Match($section.Groups['body'].Value, '(?m)^[ \t]*(?:"enabled"|''enabled''|enabled)[ \t]*=[ \t]*(true|false)[ \t]*(?:#.*)?$', 'IgnoreCase')
        if ($enabledMatch.Success) {
            $enabled = [System.Convert]::ToBoolean($enabledMatch.Groups[1].Value)
        }
        $limitMatch = [regex]::Match($section.Groups['body'].Value, '(?m)^[ \t]*(?:"max_concurrent_threads_per_session"|''max_concurrent_threads_per_session''|max_concurrent_threads_per_session)[ \t]*=[ \t]*(\d+)[ \t]*(?:#.*)?$')
        if ($limitMatch.Success) {
            $limit = [int]$limitMatch.Groups[1].Value
        }
        else {
            $legacyLimitMatch = [regex]::Match($section.Groups['body'].Value, '(?m)^[ \t]*(?:"max_threads"|''max_threads''|max_threads)[ \t]*=[ \t]*(\d+)[ \t]*(?:#.*)?$')
            if ($legacyLimitMatch.Success) {
                $limit = [int]$legacyLimitMatch.Groups[1].Value
            }
        }
    }
}

$mode = 'MANUAL (implicit Codex default)'
$unsupportedShape = $false
if (Test-Path -LiteralPath $configPath) {
    if (
        $text -match '(?m)^[ \t]*(?:"agents"|''agents''|agents)[ \t]*(?:\.|=)' -or
        $text -match '(?m)^[ \t]*\[\[[ \t]*(?:"agents"|''agents''|agents)[ \t]*\]\][ \t]*(?:#.*)?$' -or
        $text.Contains($tripleDoubleQuote) -or
        $text.Contains($tripleSingleQuote)
    ) {
        $unsupportedShape = $true
        $mode = 'UNKNOWN (unsupported agents config shape)'
    }
}
if (-not $unsupportedShape) {
    if ($enabled -eq $false) {
        $mode = 'OFF'
    }
    elseif ($enabled -eq $true) {
        $mode = 'MANUAL'
    }
}

$installed = @()
if (Test-Path -LiteralPath $agentDirectory) {
    $installed = Get-ChildItem -LiteralPath $agentDirectory -File -Filter '*.toml' | ForEach-Object {
        $match = [regex]::Match([System.IO.File]::ReadAllText($_.FullName), '(?m)^\s*name\s*=\s*"([^"]+)"\s*$')
        if ($match.Success) {
            $match.Groups[1].Value
        }
    } | Sort-Object -Unique
}

$limitText = if ($null -eq $limit) { 'Codex default' } else { [string]$limit }
$agentText = if ($installed.Count -eq 0) { 'none' } else { $installed -join ', ' }

"Current mode: $mode"
"Concurrent limit: $limitText"
"Installed agents: $agentText"
"Config source: $configPath; agent source: $agentDirectory"
'Restart/new session required: Yes after a mode change'
