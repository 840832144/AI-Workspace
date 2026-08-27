[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'CodexNetwork.Common.ps1')

Get-ChildItem -LiteralPath $PSScriptRoot -Filter '*.ps1' | ForEach-Object {
    [void][scriptblock]::Create((Get-Content -Raw -LiteralPath $_.FullName))
}

$samples = @(
    "model = `"test`"`n",
    "[features]`njs_repl = false`n",
    "[features]`nrespect_system_proxy = false`n[desktop]`n"
)
foreach ($sample in $samples) {
    $patched = Get-T17PatchedConfigText -Text $sample
    if ([regex]::Matches($patched, '(?m)^respect_system_proxy = true$').Count -ne 1) {
        throw '配置补丁回归失败：respect_system_proxy 不是唯一 true。'
    }
    $again = Get-T17PatchedConfigText -Text $patched
    if ($again -ne $patched) { throw '配置补丁回归失败：重复运行不幂等。' }
}

$ambiguousFailed = $false
try {
    [void](Get-T17PatchedConfigText -Text "[features]`n[features]`n")
} catch {
    $ambiguousFailed = $true
}
if (-not $ambiguousFailed) { throw '配置补丁回归失败：重复 section 未 fail-closed。' }

$laterConfig = "[features]`nrespect_system_proxy = true`njs_repl = false`n[projects.'later']`ntrust_level = `"trusted`"`n"
$surgical = Get-T17RestoredConfigText -Text $laterConfig -PreviousState absent -PreviousValue $null
if ($surgical -match 'respect_system_proxy' -or $surgical -notmatch "\[projects\.'later'\]") {
    throw '恢复回归失败：未只移除 TASK-0017 键或覆盖了后续配置。'
}
$restoreFalse = Get-T17RestoredConfigText -Text $laterConfig -PreviousState present -PreviousValue $false
if ($restoreFalse -notmatch '(?m)^respect_system_proxy = false$') {
    throw '恢复回归失败：不能恢复原有 false。'
}

$stateSample = '{"status":"applied"}' | ConvertFrom-Json
$stateSample.status = 'restored'
$stateSample | Add-Member -NotePropertyName restored_at -NotePropertyValue 'test' -Force
$stateSample | Add-Member -NotePropertyName restored_sha256 -NotePropertyValue 'hash' -Force
if ($stateSample.status -ne 'restored' -or $stateSample.restored_sha256 -ne 'hash') {
    throw '恢复状态回归失败：PowerShell 5.1 JSON 对象不能安全扩展。'
}

Write-Output 'TASK-0017 PowerShell syntax and config patch tests: PASS'
