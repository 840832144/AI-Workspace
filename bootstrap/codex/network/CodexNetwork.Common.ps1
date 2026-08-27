Set-StrictMode -Version 2.0

$script:T17ProxyVariables = @(
    'HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'NO_PROXY',
    'http_proxy', 'https_proxy', 'all_proxy', 'no_proxy'
)

function Get-T17CodexExecutable {
    $running = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -eq 'codex.exe' -and $_.ExecutablePath } |
        Select-Object -First 1
    if ($running) {
        return $running.ExecutablePath
    }

    $binRoot = Join-Path $env:LOCALAPPDATA 'OpenAI\Codex\bin'
    $candidate = Get-ChildItem -LiteralPath $binRoot -Filter codex.exe -Recurse -File -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1
    if (-not $candidate) {
        throw '未找到 Codex bundled CLI。请先启动 Codex Desktop，再重试。'
    }
    return $candidate.FullName
}

function Get-T17ConfigPath {
    return (Join-Path $env:USERPROFILE '.codex\config.toml')
}

function Get-T17StateRoot {
    return (Join-Path $env:LOCALAPPDATA 'AI-Workspace\codex-network')
}

function Get-T17FileHash {
    param([Parameter(Mandatory = $true)][string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) { return $null }
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash
}

function Get-T17SystemProxy {
    $internet = Get-ItemProperty 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings' -ErrorAction SilentlyContinue
    $enabled = [bool]$internet.ProxyEnable
    $server = [string]$internet.ProxyServer
    $hostLabel = '<none>'
    $port = $null
    $loopback = $false

    if ($server) {
        $matches = [regex]::Matches(
            $server,
            '(?i)(?:(?:https?|socks)=)?(?:https?://)?(?<host>\[[^\]]+\]|[^:;=\s]+):(?<port>\d+)'
        )
        foreach ($match in $matches) {
            $candidateHost = $match.Groups['host'].Value.Trim('[', ']')
            if ($candidateHost -in @('127.0.0.1', 'localhost', '::1')) {
                $hostLabel = 'loopback'
                $port = [int]$match.Groups['port'].Value
                $loopback = $true
                break
            }
        }
        if (-not $loopback) { $hostLabel = '<redacted-host>' }
    }

    $owner = $null
    if ($loopback -and $port) {
        $connection = Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction SilentlyContinue |
            Select-Object -First 1
        if ($connection) {
            $process = Get-Process -Id $connection.OwningProcess -ErrorAction SilentlyContinue
            if ($process) { $owner = $process.ProcessName }
        }
    }

    $autoConfigValue = $null
    if ($internet -and $internet.PSObject.Properties['AutoConfigURL']) {
        $autoConfigValue = $internet.AutoConfigURL
    }
    $proxyOverrideValue = $null
    if ($internet -and $internet.PSObject.Properties['ProxyOverride']) {
        $proxyOverrideValue = [string]$internet.ProxyOverride
    }

    [pscustomobject]@{
        enabled = $enabled
        source = 'WinINET'
        host = $hostLabel
        port = $port
        loopback = $loopback
        process = $owner
        auto_config = [bool]$autoConfigValue
        local_override = if ($proxyOverrideValue) {
            ($proxyOverrideValue -match 'localhost') -or
            ($proxyOverrideValue -match '127\.0\.0\.1') -or
            ($proxyOverrideValue -match '<local>')
        } else { $false }
    }
}

function Get-T17FeatureValue {
    param([Parameter(Mandatory = $true)][string]$ConfigPath)
    if (-not (Test-Path -LiteralPath $ConfigPath)) {
        return [pscustomobject]@{ state = 'missing-config'; value = $null; count = 0 }
    }

    $lines = [System.IO.File]::ReadAllLines($ConfigPath)
    $sectionCount = 0
    $keyCount = 0
    $value = $null
    $inside = $false
    foreach ($line in $lines) {
        if ($line -match '^\s*\[features\]\s*$') {
            $sectionCount++
            $inside = $true
            continue
        }
        if ($inside -and $line -match '^\s*\[') { $inside = $false }
        if ($inside -and $line -match '^\s*respect_system_proxy\s*=\s*(true|false)\s*(?:#.*)?$') {
            $keyCount++
            $value = [bool]::Parse($matches[1])
        }
    }

    if ($sectionCount -gt 1 -or $keyCount -gt 1) {
        return [pscustomobject]@{ state = 'ambiguous'; value = $null; count = $keyCount }
    }
    if ($keyCount -eq 0) {
        return [pscustomobject]@{ state = 'absent'; value = $null; count = 0 }
    }
    return [pscustomobject]@{ state = 'present'; value = $value; count = 1 }
}

function Get-T17PatchedConfigText {
    param([Parameter(Mandatory = $true)][string]$Text)

    $newline = if ($Text.Contains("`r`n")) { "`r`n" } else { "`n" }
    $hadFinalNewline = $Text.EndsWith("`n")
    $lines = @($Text -split "`r?`n")
    if ($hadFinalNewline -and $lines.Count -gt 0 -and $lines[-1] -eq '') {
        $lines = @($lines[0..($lines.Count - 2)])
    }

    $sectionIndexes = @()
    for ($index = 0; $index -lt $lines.Count; $index++) {
        if ($lines[$index] -match '^\s*\[features\]\s*$') { $sectionIndexes += $index }
    }
    if ($sectionIndexes.Count -gt 1) { throw '检测到多个 [features] section，已停止，未修改配置。' }

    $result = New-Object 'System.Collections.Generic.List[string]'
    foreach ($line in $lines) { $result.Add($line) }

    if ($sectionIndexes.Count -eq 0) {
        if ($result.Count -gt 0 -and $result[$result.Count - 1] -ne '') { $result.Add('') }
        $result.Add('[features]')
        $result.Add('respect_system_proxy = true')
    } else {
        $sectionStart = $sectionIndexes[0]
        $sectionEnd = $result.Count
        for ($index = $sectionStart + 1; $index -lt $result.Count; $index++) {
            if ($result[$index] -match '^\s*\[') { $sectionEnd = $index; break }
        }

        $keyIndexes = @()
        for ($index = $sectionStart + 1; $index -lt $sectionEnd; $index++) {
            if ($result[$index] -match '^\s*respect_system_proxy\s*=') { $keyIndexes += $index }
        }
        if ($keyIndexes.Count -gt 1) { throw '检测到多个 respect_system_proxy，已停止，未修改配置。' }
        if ($keyIndexes.Count -eq 1) {
            if ($result[$keyIndexes[0]] -notmatch '^\s*respect_system_proxy\s*=\s*(true|false)\s*(?:#.*)?$') {
                throw 'respect_system_proxy 不是可安全修改的布尔值，已停止。'
            }
            $result[$keyIndexes[0]] = 'respect_system_proxy = true'
        } else {
            $result.Insert($sectionStart + 1, 'respect_system_proxy = true')
        }
    }

    return (($result -join $newline) + $newline)
}

function Get-T17RestoredConfigText {
    param(
        [Parameter(Mandatory = $true)][string]$Text,
        [Parameter(Mandatory = $true)][string]$PreviousState,
        [AllowNull()][object]$PreviousValue
    )

    if ($PreviousState -notin @('absent', 'present')) {
        throw "无法安全恢复 previous feature state：$PreviousState"
    }

    $newline = if ($Text.Contains("`r`n")) { "`r`n" } else { "`n" }
    $lines = @($Text -split "`r?`n")
    if ($Text.EndsWith("`n") -and $lines.Count -gt 0 -and $lines[-1] -eq '') {
        $lines = @($lines[0..($lines.Count - 2)])
    }

    $sectionIndexes = @()
    for ($index = 0; $index -lt $lines.Count; $index++) {
        if ($lines[$index] -match '^\s*\[features\]\s*$') { $sectionIndexes += $index }
    }
    if ($sectionIndexes.Count -ne 1) {
        throw '当前 config.toml 的 [features] section 不唯一，不能只撤销 TASK-0017 键。'
    }

    $sectionStart = $sectionIndexes[0]
    $sectionEnd = $lines.Count
    for ($index = $sectionStart + 1; $index -lt $lines.Count; $index++) {
        if ($lines[$index] -match '^\s*\[') { $sectionEnd = $index; break }
    }
    $keyIndexes = @()
    for ($index = $sectionStart + 1; $index -lt $sectionEnd; $index++) {
        if ($lines[$index] -match '^\s*respect_system_proxy\s*=') { $keyIndexes += $index }
    }
    if ($keyIndexes.Count -ne 1 -or $lines[$keyIndexes[0]] -notmatch '^\s*respect_system_proxy\s*=\s*true\s*(?:#.*)?$') {
        throw 'respect_system_proxy 已被其他写入者改变，不能自动撤销。'
    }

    $result = New-Object 'System.Collections.Generic.List[string]'
    foreach ($line in $lines) { $result.Add($line) }
    if ($PreviousState -eq 'absent') {
        $result.RemoveAt($keyIndexes[0])
    } else {
        $restoredValue = if ([bool]$PreviousValue) { 'true' } else { 'false' }
        $result[$keyIndexes[0]] = "respect_system_proxy = $restoredValue"
    }

    return (($result -join $newline) + $newline)
}

function Write-T17TextAtomic {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Text
    )
    $directory = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $directory)) {
        New-Item -ItemType Directory -Path $directory -Force | Out-Null
    }
    $temporary = Join-Path $directory ('.task0017-' + [guid]::NewGuid().ToString('N') + '.tmp')
    $replaceBackup = Join-Path $directory ('.task0017-' + [guid]::NewGuid().ToString('N') + '.replace.bak')
    $encoding = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($temporary, $Text, $encoding)
    try {
        if (Test-Path -LiteralPath $Path) {
            [System.IO.File]::Replace($temporary, $Path, $replaceBackup)
        } else {
            Move-Item -LiteralPath $temporary -Destination $Path
        }
    } finally {
        if (Test-Path -LiteralPath $temporary) { Remove-Item -LiteralPath $temporary -Force }
        if (Test-Path -LiteralPath $replaceBackup) { Remove-Item -LiteralPath $replaceBackup -Force }
    }
}

function Invoke-T17Doctor {
    param(
        [ValidateSet('Inherit', 'None', 'Explicit')][string]$ProxyMode = 'Inherit',
        [Nullable[bool]]$RespectSystemProxy = $null,
        [string]$ExplicitProxyUrl
    )

    $codex = Get-T17CodexExecutable
    $arguments = New-Object 'System.Collections.Generic.List[string]'
    if ($null -ne $RespectSystemProxy) {
        $value = if ([bool]$RespectSystemProxy) { 'true' } else { 'false' }
        $arguments.Add('-c')
        $arguments.Add("features.respect_system_proxy=$value")
    }
    $arguments.Add('doctor')
    $arguments.Add('--all')
    $arguments.Add('--json')

    $start = New-Object System.Diagnostics.ProcessStartInfo
    $start.FileName = $codex
    $start.Arguments = ($arguments -join ' ')
    $start.UseShellExecute = $false
    $start.RedirectStandardOutput = $true
    $start.RedirectStandardError = $true
    $start.CreateNoWindow = $true

    if ($ProxyMode -in @('None', 'Explicit')) {
        foreach ($name in $script:T17ProxyVariables) { $start.EnvironmentVariables.Remove($name) }
    }
    if ($ProxyMode -eq 'Explicit') {
        if (-not $ExplicitProxyUrl) { throw 'Explicit 模式需要 loopback proxy URL。' }
        foreach ($name in @('HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'http_proxy', 'https_proxy', 'all_proxy')) {
            $start.EnvironmentVariables[$name] = $ExplicitProxyUrl
        }
        foreach ($name in @('NO_PROXY', 'no_proxy')) {
            $start.EnvironmentVariables[$name] = 'localhost,127.0.0.1,::1'
        }
    }

    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $start
    [void]$process.Start()
    $stdout = $process.StandardOutput.ReadToEnd()
    $stderr = $process.StandardError.ReadToEnd()
    $process.WaitForExit()
    $stopwatch.Stop()

    $firstBrace = $stdout.IndexOf('{')
    $lastBrace = $stdout.LastIndexOf('}')
    if ($firstBrace -lt 0 -or $lastBrace -le $firstBrace) {
        throw "Codex doctor 未返回可解析的脱敏 JSON。exit=$($process.ExitCode) stderr_present=$([bool]$stderr.Trim())"
    }
    $report = $stdout.Substring($firstBrace, $lastBrace - $firstBrace + 1) | ConvertFrom-Json
    return [pscustomobject]@{
        report = $report
        exit_code = $process.ExitCode
        elapsed_ms = $stopwatch.ElapsedMilliseconds
    }
}

function ConvertTo-T17DoctorSummary {
    param([Parameter(Mandatory = $true)]$DoctorResult)
    $report = $DoctorResult.report
    $websocket = $report.checks.'network.websocket_reachability'
    $http = $report.checks.'network.provider_reachability'
    $network = $report.checks.'network.env'
    $config = $report.checks.'config.load'

    $handshake = $null
    if ($websocket.details.PSObject.Properties['handshake result']) {
        $handshake = $websocket.details.'handshake result'
    }
    $dns = $null
    if ($websocket.details.PSObject.Properties['DNS']) { $dns = $websocket.details.DNS }
    $proxyEnvironment = 'none'
    if ($network.details.PSObject.Properties['proxy env vars present']) {
        $proxyEnvironment = $network.details.'proxy env vars present'
    }
    $respectSystemProxy = 'unknown'
    if ($network.details.PSObject.Properties['respect system proxy']) {
        $respectSystemProxy = $network.details.'respect system proxy'
    }
    $configParse = $null
    if ($config.details.PSObject.Properties['config.toml parse']) {
        $configParse = $config.details.'config.toml parse'
    }
    $httpInference = $null
    if ($http.details.PSObject.Properties['ChatGPT inference URL']) {
        $httpInference = $http.details.'ChatGPT inference URL'
    }
    $httpCdn = $null
    if ($http.details.PSObject.Properties['desktop assets CDN']) {
        $httpCdn = $http.details.'desktop assets CDN'
    }

    [pscustomobject]@{
        codex_version = $report.codexVersion
        websocket_status = $websocket.status
        websocket_summary = $websocket.summary
        websocket_handshake = $handshake
        websocket_dns = $dns
        http_status = $http.status
        http_summary = $http.summary
        http_inference = $httpInference
        http_cdn = $httpCdn
        proxy_environment = $proxyEnvironment
        respect_system_proxy = $respectSystemProxy
        config_parse = $configParse
        tls_result = if ($websocket.summary -match 'succeeded' -or $http.status -eq 'ok') {
            '未观察到证书/TLS错误'
        } else { '未确认' }
        elapsed_ms = $DoctorResult.elapsed_ms
    }
}

function Write-T17Json {
    param([Parameter(Mandatory = $true)]$Value)
    $Value | ConvertTo-Json -Depth 8
}
