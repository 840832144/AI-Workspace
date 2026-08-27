[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('Off', 'Manual')]
    [string]$Mode
)

$ErrorActionPreference = 'Stop'

function Get-ConfigPath {
    if ([string]::IsNullOrWhiteSpace($env:USERPROFILE)) {
        throw 'USERPROFILE is unavailable.'
    }

    return Join-Path $env:USERPROFILE '.codex\config.toml'
}

function Get-Newline {
    param([string]$Text)

    if ($Text.Contains("`r`n")) {
        return "`r`n"
    }

    return "`n"
}

function Set-AgentConfig {
    param(
        [string]$Text,
        [bool]$Enabled,
        [int]$MaxConcurrentThreads
    )

    $tripleDoubleQuote = '"' * 3
    $tripleSingleQuote = "'" * 3
    if ($Text.Contains($tripleDoubleQuote) -or $Text.Contains($tripleSingleQuote)) {
        throw 'Multiline TOML strings are unsupported; refusing to patch config.toml.'
    }

    $newline = Get-Newline -Text $Text
    $hadFinalNewline = $Text.EndsWith("`n")
    $lines = [System.Collections.Generic.List[string]]::new()

    if ($Text.Length -gt 0) {
        foreach ($line in [regex]::Split($Text, '\r?\n')) {
            $lines.Add($line)
        }
        if ($hadFinalNewline -and $lines.Count -gt 0 -and $lines[$lines.Count - 1] -eq '') {
            $lines.RemoveAt($lines.Count - 1)
        }
    }

    $agentsHeaderPattern = '^\s*\[\s*(?:"agents"|''agents''|agents)\s*\]\s*(?:#.*)?$'
    $agentsArrayHeaderPattern = '^\s*\[\[\s*(?:"agents"|''agents''|agents)\s*\]\]\s*(?:#.*)?$'
    $tableHeaderPattern = '^\s*\[\[?.*\]\]?\s*(?:#.*)?$'
    $unsupportedRootAgentsPattern = '^\s*(?:"agents"|''agents''|agents)\s*(?:\.|=)'
    $headerIndex = -1
    for ($index = 0; $index -lt $lines.Count; $index++) {
        if ($lines[$index] -match $agentsArrayHeaderPattern) {
            throw 'Unsupported [[agents]] array table; refusing to patch config.toml.'
        }
        elseif ($lines[$index] -match $agentsHeaderPattern) {
            if ($headerIndex -ge 0) {
                throw 'Duplicate [agents] tables found; refusing to patch config.toml.'
            }
            $headerIndex = $index
        }
        elseif ($lines[$index] -match $unsupportedRootAgentsPattern) {
            throw 'Unsupported dotted or inline agents configuration; refusing to patch config.toml.'
        }
    }

    $enabledValue = if ($Enabled) { 'true' } else { 'false' }

    if ($headerIndex -lt 0) {
        if ($lines.Count -gt 0 -and $lines[$lines.Count - 1] -ne '') {
            $lines.Add('')
        }
        $lines.Add('[agents]')
        $lines.Add("enabled = $enabledValue")
        $lines.Add("max_concurrent_threads_per_session = $MaxConcurrentThreads")
    }
    else {
        $sectionEnd = $lines.Count
        for ($index = $headerIndex + 1; $index -lt $lines.Count; $index++) {
            if ($lines[$index] -match $tableHeaderPattern) {
                $sectionEnd = $index
                break
            }
        }

        $enabledFound = $false
        $limitFound = $false
        $legacyLimitFound = $false
        $index = $headerIndex + 1
        while ($index -lt $sectionEnd) {
            $line = $lines[$index]
            if ($line -match '^(\s*)(?:"enabled"|''enabled''|enabled)\s*=.*?(\s+#.*)?$') {
                if ($enabledFound) {
                    throw 'Duplicate agents.enabled keys found; refusing to patch config.toml.'
                }
                $comment = $matches[2]
                $lines[$index] = "$($matches[1])enabled = $enabledValue$comment"
                $enabledFound = $true
            }
            elseif ($line -match '^(\s*)(?:"max_concurrent_threads_per_session"|''max_concurrent_threads_per_session''|max_concurrent_threads_per_session)\s*=.*?(\s+#.*)?$') {
                if ($limitFound) {
                    throw 'Duplicate agents.max_concurrent_threads_per_session keys found; refusing to patch config.toml.'
                }
                $comment = $matches[2]
                $lines[$index] = "$($matches[1])max_concurrent_threads_per_session = $MaxConcurrentThreads$comment"
                $limitFound = $true
            }
            elseif ($line -match '^(\s*)(?:"max_threads"|''max_threads''|max_threads)\s*=.*?(\s+#.*)?$') {
                if ($legacyLimitFound) {
                    throw 'Duplicate agents.max_threads keys found; refusing to patch config.toml.'
                }
                $comment = $matches[2]
                $lines[$index] = "$($matches[1])max_threads = $MaxConcurrentThreads$comment"
                $legacyLimitFound = $true
            }
            $index++
        }

        if (-not $enabledFound) {
            $lines.Insert($sectionEnd, "enabled = $enabledValue")
            $sectionEnd++
        }
        if (-not $limitFound) {
            $lines.Insert($sectionEnd, "max_concurrent_threads_per_session = $MaxConcurrentThreads")
        }
    }

    $result = [string]::Join($newline, $lines)
    if ($hadFinalNewline -or $Text.Length -eq 0) {
        $result += $newline
    }

    return $result
}

$configPath = Get-ConfigPath
$configDirectory = Split-Path -Parent $configPath
if (-not (Test-Path -LiteralPath $configDirectory)) {
    New-Item -ItemType Directory -Path $configDirectory -Force | Out-Null
}

$configExisted = Test-Path -LiteralPath $configPath
$backupPath = $null
$stream = $null

try {
    try {
        $stream = [System.IO.File]::Open(
            $configPath,
            [System.IO.FileMode]::OpenOrCreate,
            [System.IO.FileAccess]::ReadWrite,
            [System.IO.FileShare]::None
        )
    }
    catch {
        throw 'config.toml is in use; no changes were written. Close the competing writer and retry.'
    }

    if ($stream.Length -gt [int]::MaxValue) {
        throw 'config.toml is too large to patch safely.'
    }

    $originalBytes = New-Object byte[] ([int]$stream.Length)
    if ($originalBytes.Length -gt 0) {
        $stream.Position = 0
        $read = $stream.Read($originalBytes, 0, $originalBytes.Length)
        if ($read -ne $originalBytes.Length) {
            throw 'Could not read config.toml completely.'
        }
    }

    $hasUtf8Bom = $originalBytes.Length -ge 3 -and
        $originalBytes[0] -eq 0xEF -and
        $originalBytes[1] -eq 0xBB -and
        $originalBytes[2] -eq 0xBF
    $offset = if ($hasUtf8Bom) { 3 } else { 0 }
    $strictUtf8 = New-Object System.Text.UTF8Encoding($false, $true)
    $original = $strictUtf8.GetString($originalBytes, $offset, $originalBytes.Length - $offset)
    $enabled = $Mode -eq 'Manual'
    $updated = Set-AgentConfig -Text $original -Enabled $enabled -MaxConcurrentThreads 4
    $changed = $updated -cne $original

    if ($changed) {
        if ($configExisted) {
            $stamp = Get-Date -Format 'yyyyMMdd-HHmmss-fff'
            $backupPath = "$configPath.bak.$stamp"
            [System.IO.File]::WriteAllBytes($backupPath, $originalBytes)
        }

        $bodyBytes = $strictUtf8.GetBytes($updated)
        if ($hasUtf8Bom) {
            $updatedBytes = New-Object byte[] ($bodyBytes.Length + 3)
            $updatedBytes[0] = 0xEF
            $updatedBytes[1] = 0xBB
            $updatedBytes[2] = 0xBF
            [System.Array]::Copy($bodyBytes, 0, $updatedBytes, 3, $bodyBytes.Length)
        }
        else {
            $updatedBytes = $bodyBytes
        }

        $stream.Position = 0
        $stream.SetLength(0)
        $stream.Write($updatedBytes, 0, $updatedBytes.Length)
        $stream.Flush($true)
    }
}
finally {
    if ($null -ne $stream) {
        $stream.Dispose()
    }
}

if ($changed -and $null -ne $backupPath) {
    if (-not (Test-Path -LiteralPath $backupPath)) {
        throw 'Configuration changed but backup verification failed.'
    }
}

if ($changed -and -not (Test-Path -LiteralPath $configPath)) {
    throw 'Configuration write verification failed.'
}

if ($changed) {
    if ($configExisted -and $null -eq $backupPath) {
        throw 'Existing configuration changed without a backup.'
    }
}

"Current mode: $($Mode.ToUpperInvariant())"
'Concurrent limit: 4'
"Config source: $configPath"
if ($null -ne $backupPath) {
    "Backup: $backupPath"
}
"Config changed: $changed"
'Restart/new session required: Yes after a mode change'
if ($Mode -eq 'Manual') {
    'Safety prerequisite: MANUAL is forbidden with --yolo, full-access, danger-full-access, or equivalent permissive live permissions.'
    'Live permission detection: unavailable; keep OFF unless the parent session is confirmed restricted.'
}
