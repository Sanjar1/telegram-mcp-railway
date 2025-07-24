@echo off
echo === Setting up timed Claude Weather Test ===
echo Current time: %time%
echo Current date: %date%

REM Get current time for reference
for /f "tokens=1-3 delims=:." %%a in ("%time%") do (
    set hour=%%a
    set minute=%%b
    set second=%%c
)

echo Current time is %hour%:%minute%:%second%

REM Prompt for target time
set /p target_time="Enter target time (HH:MM format, e.g. 14:18): "

echo.
echo Setting up scheduled task for %target_time%...

REM Create the PowerShell command that will run
set ps_command=cd 'C:\Users\99893\Documents\MCP\ContextData'; Start-Process 'claude_weather_test.ps1' -WindowStyle Normal

REM Create scheduled task using schtasks
schtasks /create /tn "ClaudeWeatherTest" /tr "powershell.exe -ExecutionPolicy Bypass -Command \"%ps_command%\"" /sc once /st %target_time% /f

if %errorlevel% equ 0 (
    echo.
    echo ✅ SUCCESS: Scheduled task created!
    echo Task name: ClaudeWeatherTest
    echo Will run at: %target_time% today
    echo.
    echo The task will:
    echo   1. Open Claude Desktop
    echo   2. Check today's weather
    echo   3. Wait 3 minutes
    echo   4. Send weather to your Telegram Saved Messages
    echo.
    echo To check the task: schtasks /query /tn "ClaudeWeatherTest"
    echo To delete the task: schtasks /delete /tn "ClaudeWeatherTest" /f
) else (
    echo.
    echo ❌ ERROR: Failed to create scheduled task
    echo Make sure you're running as Administrator
)

echo.
pause
