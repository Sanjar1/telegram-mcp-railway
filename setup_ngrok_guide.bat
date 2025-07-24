@echo off
title ngrok Setup Guide
color 0E

echo.
echo ========================================
echo    🚀 ngrok Setup Guide for iOS Access
echo ========================================
echo.
echo Follow these steps to set up ngrok:
echo.
echo 1️⃣  Go to https://ngrok.com in your browser
echo 2️⃣  Sign up for a FREE account
echo 3️⃣  Download ngrok for Windows
echo 4️⃣  Extract ngrok.exe to C:\ngrok\
echo 5️⃣  Get your authtoken from ngrok dashboard
echo 6️⃣  Run: C:\ngrok\ngrok.exe config add-authtoken YOUR_TOKEN
echo 7️⃣  Start your MCP server (use start_remote_mcp.bat)
echo 8️⃣  In another terminal: C:\ngrok\ngrok.exe http 8000
echo 9️⃣  Copy the https URL and use it in Claude iOS
echo.
echo ========================================
echo    🎯 Quick Start (if ngrok is ready)
echo ========================================
echo.
echo Step 1: Start your MCP server
echo   start_remote_mcp.bat
echo.
echo Step 2: In another terminal, start ngrok
echo   C:\ngrok\ngrok.exe http 8000
echo.
echo Step 3: Copy the HTTPS URL (like https://abc123.ngrok.io)
echo.
echo Step 4: In Claude iOS, add MCP server with that URL
echo.
echo ⚠️  Important: Port 8000 is your MCP HTTP wrapper port
echo ⚠️  Keep both terminals running for remote access
echo.
pause
