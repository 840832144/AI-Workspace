[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$inputText = [Console]::In.ReadToEnd()
try {
    $hookInput = $inputText | ConvertFrom-Json -ErrorAction Stop
} catch {
    exit 0
}

# Fail-safe only: never read transcript_path or persist last_assistant_message.
# Source-side AGENTS instructions own Candidate extraction during the turn.
$stateRoot = if ($env:LOCALAPPDATA) {
    Join-Path $env:LOCALAPPDATA 'AI-Workspace\memory\hook-checks'
} else {
    Join-Path ([System.IO.Path]::GetTempPath()) 'AI-Workspace-memory-hook-checks'
}
New-Item -ItemType Directory -Path $stateRoot -Force | Out-Null
$sessionHash = [System.BitConverter]::ToString(
    [System.Security.Cryptography.SHA256]::Create().ComputeHash(
        [System.Text.Encoding]::UTF8.GetBytes([string]$hookInput.session_id)
    )
).Replace('-', '').Substring(0, 16)
$record = [ordered]@{
    schema_version = '1.0'
    status = 'memory-check-required'
    session_reference_hash = $sessionHash
    hook_event_name = [string]$hookInput.hook_event_name
    created_at = [DateTimeOffset]::UtcNow.ToString('o')
    transcript_read = $false
    candidate_written = $false
}
$target = Join-Path $stateRoot ($sessionHash + '.json')
$record | ConvertTo-Json | Set-Content -LiteralPath $target -Encoding UTF8
exit 0
