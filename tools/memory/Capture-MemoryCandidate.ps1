[CmdletBinding()]
param(
    [string]$Root,
    [string]$StateDir,
    [string]$Event,
    [string]$Title,
    [ValidateSet('decision','rule','fact','solution','skill','workflow','status','handoff','review','failure','manifest','context-pack','lesson')]
    [string]$Type,
    [ValidateSet('public','project-private','cross-project-private','local-only','unknown')]
    [string]$Scope,
    [ValidateSet('public','internal','confidential','secret','unknown')]
    [string]$Sensitivity,
    [string]$SourceHost,
    [string]$SourceProject,
    [string]$SourceActorAlias,
    [string]$SourceReference,
    [string]$RelatedTask,
    [string]$RelatedCommit,
    [ValidateRange(0, 5)]
    [int]$DurabilityScore,
    [ValidateRange(0, 5)]
    [int]$ReuseScore,
    [ValidateRange(0, 5)]
    [int]$EvidenceScore,
    [ValidateRange(0.0, 1.0)]
    [double]$Confidence,
    [string]$Summary,
    [string[]]$Evidence,
    [string[]]$Constraint,
    [string[]]$Supersedes,
    [string]$CanonicalDestination,
    [switch]$ForceOutbox,
    [switch]$GitCommit,
    [switch]$GitPush
)

$globalArguments = @()
if ($Root) { $globalArguments += @('--root', $Root) }
if ($StateDir) { $globalArguments += @('--state-dir', $StateDir) }
$captureArguments = @('capture')
$mapping = [ordered]@{
    Event = '--event'; Title = '--title'; Type = '--type'; Scope = '--scope'
    Sensitivity = '--sensitivity'; SourceHost = '--source-host'
    SourceProject = '--source-project'; SourceActorAlias = '--source-actor-alias'
    SourceReference = '--source-reference'; RelatedTask = '--related-task'
    RelatedCommit = '--related-commit'; DurabilityScore = '--durability-score'
    ReuseScore = '--reuse-score'; EvidenceScore = '--evidence-score'
    Confidence = '--confidence'; Summary = '--summary'
    CanonicalDestination = '--canonical-destination'
}
foreach ($entry in $mapping.GetEnumerator()) {
    if ($PSBoundParameters.ContainsKey($entry.Key)) {
        $captureArguments += @($entry.Value, [string](Get-Variable -Name $entry.Key -ValueOnly))
    }
}
foreach ($item in $Evidence) { $captureArguments += @('--evidence', $item) }
foreach ($item in $Constraint) { $captureArguments += @('--constraint', $item) }
foreach ($item in $Supersedes) { $captureArguments += @('--supersedes', $item) }
if ($ForceOutbox) { $captureArguments += '--force-outbox' }
if ($GitCommit) { $captureArguments += '--git-commit' }
if ($GitPush) { $captureArguments += '--git-push' }

& (Join-Path $PSScriptRoot 'Invoke-MemoryCli.ps1') @globalArguments @captureArguments
exit $LASTEXITCODE
