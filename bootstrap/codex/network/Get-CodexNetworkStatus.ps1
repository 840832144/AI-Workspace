[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'CodexNetwork.Common.ps1')

$configPath = Get-T17ConfigPath
$feature = Get-T17FeatureValue -ConfigPath $configPath
$proxy = Get-T17SystemProxy
$doctor = Invoke-T17Doctor -ProxyMode Inherit
$transport = ConvertTo-T17DoctorSummary -DoctorResult $doctor
$running = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -eq 'codex.exe' } |
    Select-Object -First 1
$configWrite = if (Test-Path -LiteralPath $configPath) { (Get-Item -LiteralPath $configPath).LastWriteTime } else { $null }
$restartRequired = $false
if ($running -and $configWrite) {
    $process = Get-Process -Id $running.ProcessId -ErrorAction SilentlyContinue
    if ($process) { $restartRequired = $process.StartTime -lt $configWrite }
}

Write-T17Json ([ordered]@{
    状态 = 'Codex 网络状态'
    Codex版本 = $transport.codex_version
    当前传输判断 = $transport.websocket_summary
    WebSocket = $transport.websocket_handshake
    HTTPS_SSE = $transport.http_inference
    可选CDN = $transport.http_cdn
    TLS = $transport.tls_result
    代理来源 = $proxy.source
    代理 = [ordered]@{
        enabled = $proxy.enabled
        host = $proxy.host
        port = $proxy.port
        process = $proxy.process
    }
    修复模式 = if ($feature.value -eq $true) { 'Codex respect_system_proxy' } else { '未应用' }
    配置来源 = "$configPath [features]"
    配置SHA256 = Get-T17FileHash -Path $configPath
    localhost = if ($proxy.local_override) { 'Windows bypass 已声明' } else { '任意 localhost HTTP bypass 未声明；当前 MCP 为 stdio，不走代理' }
    需要重启Codex = $restartRequired
    Subagents = 'none'
})
