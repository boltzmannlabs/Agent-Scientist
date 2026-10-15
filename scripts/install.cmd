@echo off
REM ============================================================================
REM Agent Scientist installation for a complete Windows source checkout
REM ============================================================================
REM From the repository root: scripts\install.cmd
REM This runs the checked-out SCI user installer, never a remote installer.
REM PowerShell users can run .\install-sci.ps1 directly; setup-sci.ps1 stays
REM the developer setup engine. See INSTALLATION.md.
REM ============================================================================

echo.
echo  Agent Scientist Setup
echo  Launching PowerShell installer...
echo.

if not exist "%~dp0..\install-sci.ps1" (
    echo Incomplete SCI checkout: install-sci.ps1 is missing. See INSTALLATION.md.
    exit /b 2
)

powershell -ExecutionPolicy ByPass -NoProfile -File "%~dp0..\install-sci.ps1" %*
exit /b %ERRORLEVEL%
