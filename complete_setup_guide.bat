@echo off
title Complete ngrok Setup for iOS Access
color 0A

echo.
echo =========================================
echo    ngrok Successfully Installed!
echo =========================================
echo.
echo Location: C:\Users\99893\AppData\Local\Microsoft\WinGet\Packages\Ngrok.Ngrok_Microsoft.Winget.Source_8wekyb3d8bbwe\ngrok.exe
echo.
echo ========================================
echo    Step 1: Get Your Authtoken
echo ========================================
echo.
echo 1. Go to https://ngrok.com
echo 2. Sign up for FREE account  
echo 3. Go to dashboard and copy your authtoken
echo 4. Come back here and run setup command
echo.
echo ========================================
echo    Step 2: Configure ngrok (run this with your token)
echo ========================================
echo.
echo "C:\Users\99893\AppData\Local\Microsoft\WinGet\Packages\Ngrok.Ngrok_Microsoft.Winget.Source_8wekyb3d8bbwe\ngrok.exe" config add-authtoken YOUR_AUTH_TOKEN_HERE
echo.
echo ========================================
echo    Step 3: Start Your Servers
echo ========================================
echo.
echo Terminal 1 - Start MCP Server:
echo   cd C:\Users\99893\Downloads\mycode\telegram-mcp
echo   python simple_mcp_wrapper.py
echo.
echo Terminal 2 - Start ngrok:
echo   "C:\Users\99893\AppData\Local\Microsoft\WinGet\Packages\Ngrok.Ngrok_Microsoft.Winget.Source_8wekyb3d8bbwe\ngrok.exe" http 8000
echo.
echo ========================================
echo    Step 4: Configure Claude iOS
echo ========================================
echo.
echo 1. Copy the HTTPS URL from ngrok (like https://abc123.ngrok.io)
echo 2. In Claude iOS: Settings -^> MCP Servers -^> Add New Server
echo 3. Enter the ngrok HTTPS URL
echo 4. Test connection
echo.
echo ⚠️  Keep both terminals running for remote access!
echo.
pause
