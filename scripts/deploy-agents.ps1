[CmdletBinding()]
param(
    [switch]$Link
)

# deploy-agents.ps1 — copy AGENTS.md and skills/ to the shared agent folder.
#
# Usage:
#   scripts/deploy-agents.ps1          # copy AGENTS.md + skills/ into ~/.agents
#   scripts/deploy-agents.ps1 -Link    # also link ~/.pi/agent/AGENTS.md to it
#
# Source of truth is this repository. The deployment target is a copy destination only.
Set-StrictMode -Version 2.0
$ErrorActionPreference = 'Stop'

function Get-FullPath([string]$Path) {
    return [IO.Path]::GetFullPath($Path)
}

function Get-RelativePath([string]$Base, [string]$Path) {
    return $Path.Substring($Base.Length).TrimStart([char[]]@([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar))
}

function Remove-DeploymentPath([string]$Path) {
    $item = Get-Item -LiteralPath $Path -Force
    if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
        Remove-Item -LiteralPath $Path -Force
    } else {
        Remove-Item -LiteralPath $Path -Force -Recurse
    }
}

$repoRoot = Get-FullPath (Join-Path $PSScriptRoot '..')
$agentHome = $env:AGENT_HOME
if ([string]::IsNullOrWhiteSpace($agentHome)) {
    $agentHome = Join-Path $HOME '.agents'
}
$target = Get-FullPath $agentHome
$homePath = Get-FullPath $HOME
$rootPath = [IO.Path]::GetPathRoot($target)

if ($target -eq $homePath -or $target -eq $rootPath) {
    throw "refusing unsafe AGENT_HOME: $agentHome"
}

$agentsSource = Join-Path $repoRoot 'AGENTS.md'
$skillsSource = Join-Path $repoRoot 'skills'
if (-not (Test-Path -LiteralPath $agentsSource -PathType Leaf)) {
    throw "AGENTS.md not found in $repoRoot"
}
if (-not (Test-Path -LiteralPath $skillsSource -PathType Container)) {
    throw "skills/ not found in $repoRoot"
}

New-Item -ItemType Directory -Path $target -Force | Out-Null
Copy-Item -LiteralPath $agentsSource -Destination (Join-Path $target 'AGENTS.md') -Force
Write-Host "copied: AGENTS.md -> $(Join-Path $target 'AGENTS.md')"

# Mirror skills/: remove stale copies only inside <target>/skills.
$skillsTarget = Join-Path $target 'skills'
New-Item -ItemType Directory -Path $skillsTarget -Force | Out-Null
$sourceItems = @(Get-ChildItem -LiteralPath $skillsSource -Recurse -Force)
$sourceRelativePaths = @{}
foreach ($item in $sourceItems) {
    $sourceRelativePaths[(Get-RelativePath $skillsSource $item.FullName)] = $true
}

$targetItems = @(Get-ChildItem -LiteralPath $skillsTarget -Recurse -Force | Sort-Object { $_.FullName.Length } -Descending)
foreach ($item in $targetItems) {
    $relativePath = Get-RelativePath $skillsTarget $item.FullName
    if (-not $sourceRelativePaths.ContainsKey($relativePath)) {
        Remove-DeploymentPath $item.FullName
    }
}

foreach ($item in $sourceItems) {
    $relativePath = Get-RelativePath $skillsSource $item.FullName
    $destination = Join-Path $skillsTarget $relativePath
    if ($item.PSIsContainer) {
        New-Item -ItemType Directory -Path $destination -Force | Out-Null
    } else {
        $parent = Split-Path -Parent $destination
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
        Copy-Item -LiteralPath $item.FullName -Destination $destination -Force
    }
}

$skillCount = @(Get-ChildItem -LiteralPath $skillsTarget -Recurse -Filter 'SKILL.md' -File).Count
Write-Host "mirrored: skills/ -> $skillsTarget ($skillCount skills)"

if ($Link) {
    $piDir = Join-Path $HOME '.pi\agent'
    $piAgents = Join-Path $piDir 'AGENTS.md'
    New-Item -ItemType Directory -Path $piDir -Force | Out-Null

    $existing = Get-Item -LiteralPath $piAgents -Force -ErrorAction SilentlyContinue
    if ($null -ne $existing -and (($existing.Attributes -band [IO.FileAttributes]::ReparsePoint) -eq 0)) {
        throw "refusing to overwrite real file $piAgents (not a symlink)"
    }
    if ($null -ne $existing) {
        Remove-DeploymentPath $piAgents
    }
    New-Item -ItemType SymbolicLink -Path $piAgents -Target (Join-Path $target 'AGENTS.md') | Out-Null
    Write-Host "linked: $piAgents -> $(Join-Path $target 'AGENTS.md')"
}

Write-Host 'done.'
