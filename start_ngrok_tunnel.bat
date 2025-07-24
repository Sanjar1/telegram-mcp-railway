@echo off
title Start ngrok Tunnel
color 0E

echo.
echo ========================================
echo    Starting ngrok Tunnel for iOS Access
echo ========================================
echo.
echo Exposing local port 8000 to the internet...
echo.
echo ⚠️  Make sure your MCP server is running first!
echo ⚠️  Copy the HTTPS URL for Claude iOS!
echo.

"C:\Users\99893\AppData\Local\Microsoft\WinGet\Packages\Ngrok.Ngrok_Microsoft.Winget.Source_8wekyb3d8bbwe\ngrok.exe" http 8000

echo.
echo 👋 ngrok tunnel stopped
pause
