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

function Get-CanonicalPath([string]$Path) {
    $fullPath = Get-FullPath $Path
    $missing = @()
    $current = $fullPath
    while ($null -eq (Get-ExistingItem $current)) {
        $leaf = Split-Path -Leaf $current
        if ([string]::IsNullOrEmpty($leaf)) {
            throw "cannot resolve path: $Path"
        }
        $missing = @($leaf) + $missing
        $current = Split-Path -Parent $current
    }
    $canonical = (Resolve-Path -LiteralPath $current).Path
    foreach ($part in $missing) {
        $canonical = Join-Path $canonical $part
    }
    return $canonical
}

function Remove-DeploymentPath([string]$Path) {
    $item = Get-Item -LiteralPath $Path -Force
    if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
        Remove-Item -LiteralPath $Path -Force
    } else {
        Remove-Item -LiteralPath $Path -Force -Recurse
    }
}

function Get-ExistingItem([string]$Path) {
    return Get-Item -LiteralPath $Path -Force -ErrorAction SilentlyContinue
}

function Assert-NotReparsePoint([string]$Path) {
    $item = Get-ExistingItem $Path
    if ($null -ne $item -and (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)) {
        throw "refusing symlinked destination: $Path"
    }
    return $item
}

$repoRoot = Get-FullPath (Join-Path $PSScriptRoot '..')
$agentHome = $env:AGENT_HOME
if ([string]::IsNullOrWhiteSpace($agentHome)) {
    $agentHome = Join-Path $HOME '.agents'
}
$targetInput = Get-FullPath $agentHome
Assert-NotReparsePoint $targetInput | Out-Null
$target = Get-CanonicalPath $targetInput
$homePath = Get-CanonicalPath $HOME
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

$targetItem = Assert-NotReparsePoint $target
if ($null -ne $targetItem -and -not $targetItem.PSIsContainer) {
    throw "AGENT_HOME is not a directory: $target"
}
$agentsTarget = Join-Path $target 'AGENTS.md'
$agentsItem = Assert-NotReparsePoint $agentsTarget
if ($null -ne $agentsItem -and $agentsItem.PSIsContainer) {
    throw "destination is not a regular file: $agentsTarget"
}
$skillsTarget = Join-Path $target 'skills'
$skillsItem = Assert-NotReparsePoint $skillsTarget
if ($null -ne $skillsItem -and -not $skillsItem.PSIsContainer) {
    throw "destination is not a directory: $skillsTarget"
}
if ($Link) {
    $piDir = Join-Path $HOME '.pi\agent'
    $piDirItem = Assert-NotReparsePoint $piDir
    if ($null -ne $piDirItem -and -not $piDirItem.PSIsContainer) {
        throw "pi agent path is not a directory: $piDir"
    }
    $piAgents = Join-Path $piDir 'AGENTS.md'
    $existing = Get-ExistingItem $piAgents
    if ($null -ne $existing -and (($existing.Attributes -band [IO.FileAttributes]::ReparsePoint) -eq 0)) {
        throw "refusing to overwrite real file $piAgents (not a symlink)"
    }
}

New-Item -ItemType Directory -Path $target -Force | Out-Null
Copy-Item -LiteralPath $agentsSource -Destination $agentsTarget -Force
Write-Host "copied: AGENTS.md -> $agentsTarget"

# Mirror skills/: remove stale copies only inside <target>/skills.
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
    New-Item -ItemType Directory -Path $piDir -Force | Out-Null

    $existing = Get-ExistingItem $piAgents
    if ($null -ne $existing) {
        Remove-DeploymentPath $piAgents
    }
    New-Item -ItemType SymbolicLink -Path $piAgents -Target (Join-Path $target 'AGENTS.md') | Out-Null
    Write-Host "linked: $piAgents -> $(Join-Path $target 'AGENTS.md')"
}

Write-Host 'done.'
