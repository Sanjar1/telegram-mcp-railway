@echo off
title Remote MCP Server
color 0A

echo.
echo 🚀 Starting Remote MCP Server...
echo ================================
echo.

cd /d "C:\Users\99893\Downloads\mycode\telegram-mcp"

echo 📦 Installing dependencies...
pip install fastapi uvicorn python-multipart
echo.

echo 🔧 Starting HTTP wrapper for your telegram-mcp...
echo 📱 This will make your MCP server accessible from Claude mobile!
echo.
echo 💡 Your existing telegram-mcp will run inside this wrapper
echo 🌐 Access via Tailscale for remote connection
echo.
echo ⏹️  Press Ctrl+C to stop the server
echo.

python mcp_http_wrapper.py

echo.
echo 👋 Remote MCP Server stopped
pause