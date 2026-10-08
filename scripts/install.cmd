@echo off
REM ============================================================================
REM Agent Scientist setup for a complete Windows source checkout
REM ============================================================================
REM From the repository root: scripts\install.cmd
REM This runs the checked-out SCI setup script, never a remote installer.
REM PowerShell users can run .\setup-sci.ps1 directly. See INSTALLATION.md.
REM ============================================================================

echo.
echo  Agent Scientist Setup
echo  Launching PowerShell installer...
echo.

if not exist "%~dp0..\setup-sci.ps1" (
    echo Incomplete SCI checkout: setup-sci.ps1 is missing. See INSTALLATION.md.
    exit /b 2
)

powershell -ExecutionPolicy ByPass -NoProfile -File "%~dp0..\setup-sci.ps1" %*
exit /b %ERRORLEVEL%
