[CmdletBinding()]
param(
    [switch]$Link
)
Set-StrictMode -Version 2.0
$ErrorActionPreference = 'Stop'

$script = Join-Path $PSScriptRoot 'deploy_agents.py'
$argsList = @()
if ($Link) {
    $argsList += '--link'
}

$pythonCandidate = $null
foreach ($cmd in @('python', 'python3', 'py')) {
    $c = Get-Command $cmd -ErrorAction SilentlyContinue
    if ($null -ne $c) {
        try {
            $null = & $c.Source -c "import sys; sys.exit(0)" 2>$null
            if ($LASTEXITCODE -eq 0) {
                $pythonCandidate = $c.Source
                break
            }
        } catch {
            # continue checking
        }
    }
}
if ($null -eq $pythonCandidate) {
    throw "a working python interpreter was not found in PATH"
}

& $pythonCandidate $script @argsList
exit $LASTEXITCODE
