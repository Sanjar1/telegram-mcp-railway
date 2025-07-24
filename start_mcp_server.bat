@echo off
title Start MCP Server for iOS
color 0A

echo.
echo ========================================
echo    Starting MCP Server for iOS Access
echo ========================================
echo.
echo Server running on: http://localhost:8000
echo Health check: http://localhost:8000/health
echo.
echo ⚠️  Keep this terminal open!
echo ⚠️  Start ngrok in another terminal!
echo.

cd /d "C:\Users\99893\Downloads\mycode\telegram-mcp"
python simple_mcp_wrapper.py

echo.
echo 👋 MCP Server stopped
pause
