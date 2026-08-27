[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'CodexNetwork.Common.ps1')

$configPath = Get-T17ConfigPath
$stateRoot = Get-T17StateRoot
$statePath = Join-Path $stateRoot 'repair-state.json'
$feature = Get-T17FeatureValue -ConfigPath $configPath
if ($feature.state -eq 'ambiguous') {
    throw 'config.toml 中 [features] 或 respect_system_proxy 不唯一，已停止。'
}

$proxy = Get-T17SystemProxy
if (-not $proxy.enabled -or -not $proxy.loopback -or -not $proxy.port) {
    throw '未检测到启用中的 loopback WinINET proxy；不会猜测或写入配置。'
}

$preflight = Invoke-T17Doctor -ProxyMode None -RespectSystemProxy $true
$preflightSummary = ConvertTo-T17DoctorSummary -DoctorResult $preflight
if ($preflightSummary.websocket_status -ne 'ok' -or $preflightSummary.websocket_handshake -notmatch '101') {
    throw '当前版本的 respect_system_proxy 预检未获得 HTTP 101；未修改配置。'
}

if ($feature.value -eq $true) {
    $current = Invoke-T17Doctor -ProxyMode Inherit
    $currentSummary = ConvertTo-T17DoctorSummary -DoctorResult $current
    Write-T17Json ([ordered]@{
        状态 = '已应用，无需重复修改'
        修复 = 'features.respect_system_proxy=true'
        WebSocket = $currentSummary.websocket_handshake
        HTTPS_SSE = $currentSummary.http_inference
        需要重启Codex = $false
    })
    exit 0
}

if (-not (Test-Path -LiteralPath $stateRoot)) {
    New-Item -ItemType Directory -Path $stateRoot -Force | Out-Null
}
$backupRoot = Join-Path (Split-Path -Parent $configPath) 'backups\task-0017-network'
if (-not (Test-Path -LiteralPath $backupRoot)) {
    New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null
}
$stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssfffZ')
$backupPath = Join-Path $backupRoot "config.toml.$stamp.bak"
$beforeHash = Get-T17FileHash -Path $configPath
Copy-Item -LiteralPath $configPath -Destination $backupPath -ErrorAction Stop

$writeStarted = $false
try {
    $originalText = [System.IO.File]::ReadAllText($configPath)
    $patchedText = Get-T17PatchedConfigText -Text $originalText
    if ((Get-T17FileHash -Path $configPath) -ne $beforeHash) {
        throw 'config.toml 在备份后被其他进程修改；未写入修复。'
    }
    $writeStarted = $true
    Write-T17TextAtomic -Path $configPath -Text $patchedText

    $current = Invoke-T17Doctor -ProxyMode None
    $currentSummary = ConvertTo-T17DoctorSummary -DoctorResult $current
    if ($currentSummary.config_parse -ne 'ok' -or $currentSummary.websocket_status -ne 'ok' -or $currentSummary.websocket_handshake -notmatch '101') {
        throw '修改后 transport 验证未通过。'
    }

    $state = [ordered]@{
        schema_version = '1.0'
        status = 'applied'
        applied_at = (Get-Date).ToUniversalTime().ToString('o')
        mode = 'respect_system_proxy'
        config_path = $configPath
        backup_path = $backupPath
        before_sha256 = $beforeHash
        after_sha256 = Get-T17FileHash -Path $configPath
        previous_feature_state = $feature.state
        previous_feature_value = $feature.value
        proxy_source = $proxy.source
        proxy_host = $proxy.host
        proxy_port = $proxy.port
        proxy_process = $proxy.process
    }
    $stateText = ($state | ConvertTo-Json -Depth 6) + [Environment]::NewLine
    Write-T17TextAtomic -Path $statePath -Text $stateText

    Write-T17Json ([ordered]@{
        状态 = '修复成功'
        修复 = 'features.respect_system_proxy=true'
        备份 = $backupPath
        WebSocket = $currentSummary.websocket_handshake
        HTTPS_SSE = $currentSummary.http_inference
        localhost = 'MCP 为 stdio，不经 HTTP proxy；未修改 Windows 全局 bypass'
        需要重启Codex = $true
        恢复命令 = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$PSScriptRoot\Restore-CodexNetworkConfig.ps1`""
    })
} catch {
    if ($writeStarted) {
        Copy-Item -LiteralPath $backupPath -Destination $configPath -Force
        throw "修复失败，已自动恢复原配置：$($_.Exception.Message)"
    }
    throw "修复在写入前停止：$($_.Exception.Message)"
}
