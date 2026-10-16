# Install Agent Scientist from this source checkout using its managed runtime.
# Windows twin of install-sci.sh; the setup engine is setup-sci.ps1.
param(
    [switch]$NonInteractive,
    [switch]$Help,
    [Parameter(ValueFromRemainingArguments = $true)][string[]]$Rest
)
$ErrorActionPreference = 'Stop'

function Show-Usage {
    Write-Output 'Usage: .\install-sci.ps1 [-NonInteractive] [-Help]'
    Write-Output ''
    Write-Output 'Installs the managed Python/tools, application dependencies, SCI launchers'
    Write-Output 'and bundled skills. Interactive mode then opens model/provider setup.'
    Write-Output '-NonInteractive installs the software without asking for credentials.'
}
if ($Help) { Show-Usage; exit 0 }
if ($Rest) {
    [Console]::Error.WriteLine("Unknown option: $($Rest -join ' ')")
    Show-Usage | ForEach-Object { [Console]::Error.WriteLine($_) }
    exit 2
}

if ([System.Environment]::OSVersion.Platform -ne [System.PlatformID]::Win32NT) {
    [Console]::Error.WriteLine('Use install-sci.sh for Linux and macOS. This installer supports native Windows.')
    exit 1
}

$sourceDir = $PSScriptRoot
foreach ($file in 'setup-sci.ps1', 'pyproject.toml', 'uv.lock', 'pm/lock.json') {
    if (-not (Test-Path -LiteralPath (Join-Path $sourceDir $file))) {
        [Console]::Error.WriteLine("Incomplete SCI checkout: $file is missing. Obtain the complete repository and retry.")
        exit 1
    }
}

$setup = -not $NonInteractive
if ($setup -and ([Console]::IsInputRedirected -or [Console]::IsOutputRedirected)) {
    Write-Output 'No interactive terminal detected; installing software without credential setup.'
    $setup = $false
}

# Mirrors install-sci.sh's ERR trap: every failure names its stage and
# preserves the child's exit code; a stopped installer is never "successful".
$script:stage = 'checking prerequisites'
function Stop-Install([int]$Code) {
    if ($Code -eq 0) { $Code = 1 }
    [Console]::Error.WriteLine('')
    [Console]::Error.WriteLine("Installation stopped during $($script:stage) (exit $Code). See the error above.")
    exit $Code
}

Write-Output 'Agent Scientist installation'
Write-Output "Source: $sourceDir"

$script:stage = 'installing runtime and dependencies'
# A child process (not dot-sourcing or &) keeps the engine's exit/throw
# behavior out of this wrapper and preserves its exact exit code.
$psHost = (Get-Process -Id $PID).Path
& $psHost -NoProfile -ExecutionPolicy Bypass -File (Join-Path $sourceDir 'setup-sci.ps1') -UserInstall
if ($LASTEXITCODE -ne 0) { Stop-Install $LASTEXITCODE }

$script:stage = 'checking the installed CLI'
$installedCli = @('sci.exe', 'sci.cmd') |
    ForEach-Object { Join-Path $sourceDir ".sci\bin\$_" } |
    Where-Object { Test-Path -LiteralPath $_ } |
    Select-Object -First 1
if (-not $installedCli) {
    [Console]::Error.WriteLine('The checkout-local launcher .sci\bin\sci is missing.')
    Stop-Install 1
}
& $installedCli --help > $null
if ($LASTEXITCODE -ne 0) { Stop-Install $LASTEXITCODE }

if ($setup) {
    $script:stage = 'configuring your model provider'
    & $installedCli setup
    if ($LASTEXITCODE -ne 0) { Stop-Install $LASTEXITCODE }
} else {
    Write-Output ''
    Write-Output 'Software installed. Configure your model before chatting: sci setup'
}

$binDir = if ($env:SCI_HOME) { Join-Path $env:SCI_HOME 'bin' } else { Join-Path $env:LOCALAPPDATA 'sci\bin' }
Write-Output ''
Write-Output 'Agent Scientist is installed.'
Write-Output 'Start: agent-sci'
Write-Output 'If the command is not found, open a new terminal or add this directory to PATH:'
Write-Output "  $binDir"
Write-Output "Keep this source checkout at: $sourceDir"
Write-Output 'Optional service credentials are configured separately inside SCI.'
