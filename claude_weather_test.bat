@echo off
echo Starting Claude Weather Test Automation...
echo Time: %date% %time%

REM Find and start Claude Desktop
echo Looking for Claude Desktop...

REM Try common installation paths
if exist "%LOCALAPPDATA%\Claude\Claude.exe" (
    echo Found Claude at: %LOCALAPPDATA%\Claude\Claude.exe
    start "" "%LOCALAPPDATA%\Claude\Claude.exe"
    goto :found
)

if exist "%APPDATA%\Claude\Claude.exe" (
    echo Found Claude at: %APPDATA%\Claude\Claude.exe
    start "" "%APPDATA%\Claude\Claude.exe"
    goto :found
)

if exist "C:\Program Files\Claude\Claude.exe" (
    echo Found Claude at: C:\Program Files\Claude\Claude.exe
    start "" "C:\Program Files\Claude\Claude.exe"
    goto :found
)

if exist "C:\Program Files (x86)\Claude\Claude.exe" (
    echo Found Claude at: C:\Program Files (x86)\Claude\Claude.exe
    start "" "C:\Program Files (x86)\Claude\Claude.exe"
    goto :found
)

REM If not found, try to start from PATH
echo Trying to start Claude from PATH...
start claude
goto :found

:found
echo Claude Desktop started successfully!
echo Test automation initiated at %time%

REM Wait 10 seconds for Claude to fully load
echo Waiting 10 seconds for Claude to load...
timeout /t 10 /nobreak

REM Create a trigger file that our automation can monitor
echo %date% %time% > "C:\Users\99893\Documents\MCP\ContextData\claude_test_trigger.txt"
echo Weather test triggered > "C:\Users\99893\Documents\MCP\ContextData\weather_test_status.txt"

echo Test automation script completed.
pause
