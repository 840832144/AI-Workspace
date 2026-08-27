[CmdletBinding()]
param(
    [ValidateSet('Baseline', 'SystemProxy', 'ExplicitProxy', 'Current')]
    [string]$Mode = 'Current'
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'CodexNetwork.Common.ps1')

$proxy = Get-T17SystemProxy
switch ($Mode) {
    'Baseline' {
        $doctor = Invoke-T17Doctor -ProxyMode None -RespectSystemProxy $false
    }
    'SystemProxy' {
        $doctor = Invoke-T17Doctor -ProxyMode None -RespectSystemProxy $true
    }
    'ExplicitProxy' {
        if (-not $proxy.enabled -or -not $proxy.loopback -or -not $proxy.port) {
            throw '未检测到可安全使用的 loopback WinINET proxy。'
        }
        $doctor = Invoke-T17Doctor -ProxyMode Explicit -RespectSystemProxy $false -ExplicitProxyUrl "http://127.0.0.1:$($proxy.port)"
    }
    default {
        $doctor = Invoke-T17Doctor -ProxyMode Inherit
    }
}

$summary = ConvertTo-T17DoctorSummary -DoctorResult $doctor
Write-T17Json ([ordered]@{
    测试 = 'Codex Transport Matrix'
    模式 = $Mode
    代理来源 = $proxy.source
    代理进程 = $proxy.process
    代理端口 = $proxy.port
    WebSocket状态 = $summary.websocket_status
    WebSocket结果 = $summary.websocket_summary
    WebSocket握手 = $summary.websocket_handshake
    DNS = $summary.websocket_dns
    HTTPS_SSE状态 = $summary.http_status
    HTTPS_SSE结果 = $summary.http_inference
    可选CDN = $summary.http_cdn
    TLS = $summary.tls_result
    respect_system_proxy = $summary.respect_system_proxy
    proxy_environment = $summary.proxy_environment
    耗时毫秒 = $summary.elapsed_ms
})

if ($summary.websocket_status -ne 'ok' -or $summary.http_status -notin @('ok', 'warning')) { exit 1 }
