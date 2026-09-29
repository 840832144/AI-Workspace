$ProgressPreference = 'SilentlyContinue'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "=== DeepSeek API Connectivity Test ==="
Write-Host ""

# Test 1: Network connectivity to DeepSeek API
Write-Host "[1/3] Testing network connectivity..."
try {
    $resp = Invoke-WebRequest -Uri 'https://api.deepseek.com/v1' -Method GET -UseBasicParsing -TimeoutSec 10
    Write-Host "  HTTP Status: $($resp.StatusCode)" -ForegroundColor Green
    $content = $resp.Content
    if ($content.Length -gt 200) { $content = $content.Substring(0, 200) }
    Write-Host "  Response: $content" -ForegroundColor Gray
} catch {
    Write-Host "  FAILED: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        Write-Host "  HTTP Status: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Red
    }
}

Write-Host ""

# Test 2: DNS resolution
Write-Host "[2/3] Testing DNS resolution..."
try {
    $dns = Resolve-DnsName -Name 'api.deepseek.com' -Type A -ErrorAction Stop
    Write-Host "  Resolved: $($dns[0].IPAddress)" -ForegroundColor Green
} catch {
    Write-Host "  DNS FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 3: Proxy settings
Write-Host "[3/3] Checking proxy settings..."
$envProxy = $env:HTTP_PROXY
$envHttpsProxy = $env:HTTPS_PROXY
$winProxy = Get-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings' -ErrorAction SilentlyContinue

if ($envProxy) { Write-Host "  HTTP_PROXY env: $envProxy" -ForegroundColor Yellow }
else { Write-Host "  HTTP_PROXY env: (not set)" -ForegroundColor Green }

if ($envHttpsProxy) { Write-Host "  HTTPS_PROXY env: $envHttpsProxy" -ForegroundColor Yellow }
else { Write-Host "  HTTPS_PROXY env: (not set)" -ForegroundColor Green }

if ($winProxy.ProxyEnable -eq 1) {
    Write-Host "  Windows Proxy: ENABLED" -ForegroundColor Yellow
    Write-Host "  Proxy Server: $($winProxy.ProxyServer)" -ForegroundColor Yellow
} else {
    Write-Host "  Windows Proxy: disabled" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== Test Complete ==="
