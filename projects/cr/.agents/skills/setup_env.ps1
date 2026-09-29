<#
.SYNOPSIS
    设置 Cash Royal 数值策划 AI 模型的环境变量。
.DESCRIPTION
    此脚本用于设置 DeepSeek API Key 等环境变量。
    支持两种模式：
    1. 用户级永久环境变量（推荐，重启后仍有效）
    2. 当前会话临时环境变量（仅当前 PowerShell 窗口有效）
.USAGE
    # 设置永久环境变量
    .\setup_env.ps1 -ApiKey "your_api_key_here"
    
    # 设置当前会话临时环境变量
    .\setup_env.ps1 -ApiKey "your_api_key_here" -SessionOnly
    
    # 清除环境变量
    .\setup_env.ps1 -Clear
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$ApiKey,
    
    [Parameter(Mandatory=$false)]
    [switch]$SessionOnly,
    
    [Parameter(Mandatory=$false)]
    [switch]$Clear
)

$ErrorActionPreference = "Stop"

# 检查是否以管理员权限运行
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if ($Clear) {
    Write-Host "正在清除环境变量..." -ForegroundColor Yellow
    [Environment]::SetEnvironmentVariable("DEEPSEEK_API_KEY", $null, "User")
    Write-Host "✓ 已清除 DEEPSEEK_API_KEY 用户级环境变量" -ForegroundColor Green
    
    # 清除当前会话
    if ($env:DEEPSEEK_API_KEY) {
        Remove-Item Env:\DEEPSEEK_API_KEY -ErrorAction SilentlyContinue
        Write-Host "✓ 已清除 DEEPSEEK_API_KEY 会话环境变量" -ForegroundColor Green
    }
    exit 0
}

if (-not $ApiKey) {
    # 交互式输入
    $ApiKey = Read-Host "请输入你的 DeepSeek API Key"
}

if ([string]::IsNullOrWhiteSpace($ApiKey)) {
    Write-Error "API Key 不能为空！"
    exit 1
}

# 验证 API Key 格式（简单检查）
if ($ApiKey -notmatch '^[a-zA-Z0-9_\-\.]+$') {
    Write-Warning "API Key 格式可能不正确，请确认。"
}

if ($SessionOnly) {
    # 设置当前会话临时环境变量
    $env:DEEPSEEK_API_KEY = $ApiKey
    Write-Host "✓ 已设置 DEEPSEEK_API_KEY 为当前会话环境变量" -ForegroundColor Green
    Write-Host "  注意：关闭此 PowerShell 窗口后变量将失效" -ForegroundColor Yellow
} else {
    # 设置用户级永久环境变量
    [Environment]::SetEnvironmentVariable("DEEPSEEK_API_KEY", $ApiKey, "User")
    Write-Host "✓ 已设置 DEEPSEEK_API_KEY 为用户级永久环境变量" -ForegroundColor Green
    Write-Host "  作用域：当前用户" -ForegroundColor Cyan
    Write-Host "  注意：需要重新打开 TRAE 才能生效" -ForegroundColor Yellow
}

# 验证设置
$verifyKey = if ($SessionOnly) { $env:DEEPSEEK_API_KEY } else { [Environment]::GetEnvironmentVariable("DEEPSEEK_API_KEY", "User") }
if ($verifyKey) {
    $maskedKey = $verifyKey.Substring(0, [Math]::Min(8, $verifyKey.Length)) + "*" * [Math]::Max(0, $verifyKey.Length - 8)
    Write-Host "✓ 验证成功：$maskedKey" -ForegroundColor Green
} else {
    Write-Error "验证失败，环境变量可能未正确设置。"
    exit 1
}

Write-Host "`n配置完成！你现在可以：" -ForegroundColor Cyan
Write-Host "  1. 重新打开 TRAE IDE" -ForegroundColor White
Write-Host "  2. 使用 .agents/skills 中的 AI Agent" -ForegroundColor White
