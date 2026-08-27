[CmdletBinding()]
param([switch]$Force)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'CodexNetwork.Common.ps1')

$statePath = Join-Path (Get-T17StateRoot) 'repair-state.json'
if (-not (Test-Path -LiteralPath $statePath)) {
    throw '没有找到 TASK-0017 repair state；未修改配置。'
}
$state = Get-Content -Raw -LiteralPath $statePath | ConvertFrom-Json
if ($state.status -ne 'applied') {
    throw "当前 repair state 不是 applied：$($state.status)"
}
if (-not (Test-Path -LiteralPath $state.backup_path)) {
    throw '原配置备份不存在；未修改配置。'
}

$currentHash = Get-T17FileHash -Path $state.config_path
$restoreMode = 'exact-backup'
$restoreText = [System.IO.File]::ReadAllText($state.backup_path)
if (-not $Force -and $currentHash -ne $state.after_sha256) {
    $currentText = [System.IO.File]::ReadAllText($state.config_path)
    $restoreText = Get-T17RestoredConfigText `
        -Text $currentText `
        -PreviousState $state.previous_feature_state `
        -PreviousValue $state.previous_feature_value
    $restoreMode = 'surgical-preserve-later-changes'
}

$stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssfffZ')
$preRestore = "$($state.config_path).pre-restore.$stamp.bak"
Copy-Item -LiteralPath $state.config_path -Destination $preRestore -ErrorAction Stop

$writeStarted = $false
try {
    if ((Get-T17FileHash -Path $state.config_path) -ne $currentHash) {
        throw 'config.toml 在恢复快照后被其他进程修改；未写入恢复。'
    }
    $writeStarted = $true
    Write-T17TextAtomic -Path $state.config_path -Text $restoreText
    $doctor = Invoke-T17Doctor -ProxyMode Inherit
    $summary = ConvertTo-T17DoctorSummary -DoctorResult $doctor
    if ($summary.config_parse -ne 'ok') { throw '恢复后 config.toml parse 失败。' }

    $state.status = 'restored'
    $state | Add-Member -NotePropertyName restored_at -NotePropertyValue ((Get-Date).ToUniversalTime().ToString('o')) -Force
    $state | Add-Member -NotePropertyName restored_sha256 -NotePropertyValue (Get-T17FileHash -Path $state.config_path) -Force
    $state | Add-Member -NotePropertyName restore_mode -NotePropertyValue $restoreMode -Force
    Write-T17TextAtomic -Path $statePath -Text (($state | ConvertTo-Json -Depth 6) + [Environment]::NewLine)

    Write-T17Json ([ordered]@{
        状态 = '已恢复修改前配置'
        恢复模式 = $restoreMode
        当前SHA256 = $state.restored_sha256
        恢复前快照 = $preRestore
        WebSocket = $summary.websocket_summary
        HTTPS_SSE = $summary.http_inference
        需要重启Codex = $true
    })
} catch {
    if ($writeStarted) {
        Copy-Item -LiteralPath $preRestore -Destination $state.config_path -Force
        throw "恢复验证失败，已回到恢复前状态：$($_.Exception.Message)"
    }
    throw "恢复在写入前停止：$($_.Exception.Message)"
}
