#!/usr/bin/env python3
"""
Enhanced HTTP Wrapper for Telegram MCP Server
Provides REST API and WebSocket endpoints for remote access
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Pydantic models
class MCPRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[str] = None
    method: str
    params: Optional[Dict[str, Any]] = None

class ToolCall(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]

# FastAPI app
app = FastAPI(
    title="Telegram MCP Remote Server",
    description="Remote access to local Telegram MCP server",
    version="1.0.0"
)

# CORS for web access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MCPServerManager:
    """Enhanced MCP server process manager"""
    
    def __init__(self):
        self.process = None
        self.stdin = None
        self.stdout = None
        self.stderr = None
        self.is_running = False
        self.tools_cache = []
        
    async def start_mcp_server(self):
        """Start the Telegram MCP server"""
        try:
            # Get current directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Command to start MCP server
            cmd = [
                sys.executable,  # Use current Python interpreter
                os.path.join(current_dir, "main.py")
            ]
            
            logger.info(f"Starting MCP server: {' '.join(cmd)}")
            logger.info(f"Working directory: {current_dir}")
            
            self.process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=current_dir
            )
            
            self.stdin = self.process.stdin
            self.stdout = self.process.stdout
            self.stderr = self.process.stderr
            self.is_running = True
            
            # Initialize with handshake
            await self._initialize_mcp()
            
            logger.info("MCP server started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start MCP server: {e}")
            self.is_running = False
            return False
    
    async def _initialize_mcp(self):
        """Initialize MCP connection and get tools"""
        try:
            # Send initialize request
            init_request = {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "clientInfo": {
                        "name": "telegram-mcp-remote",
                        "version": "1.0.0"
                    }
                }
            }
            
            response = await self.send_message(init_request)
            logger.info(f"Initialize response: {response}")
            
            # Get tools list
            tools_request = {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "tools/list"
            }
            
            tools_response = await self.send_message(tools_request)
            if "result" in tools_response and "tools" in tools_response["result"]:
                self.tools_cache = tools_response["result"]["tools"]
                logger.info(f"Loaded {len(self.tools_cache)} tools")
            
        except Exception as e:
            logger.error(f"Error initializing MCP: {e}")
    
    async def send_message(self, message: Dict) -> Dict:
        """Send message to MCP server and get response"""
        if not self.is_running or not self.stdin or not self.stdout:
            raise Exception("MCP server not running")
        
        try:
            # Send message
            message_str = json.dumps(message) + "\n"
            self.stdin.write(message_str.encode())
            await self.stdin.drain()
            
            # Read response
            response_line = await asyncio.wait_for(
                self.stdout.readline(), 
                timeout=30.0  # 30 second timeout
            )
            
            if response_line:
                response = json.loads(response_line.decode().strip())
                return response
            else:
                raise Exception("No response from MCP server")
                
        except asyncio.TimeoutError:
            logger.error("Timeout waiting for MCP response")
            raise Exception("MCP server timeout")
        except Exception as e:
            logger.error(f"Error communicating with MCP server: {e}")
            raise
    
    async def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict:
        """Call a specific tool"""
        request = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": parameters
            }
        }
        
        return await self.send_message(request)
    
    async def stop(self):
        """Stop the MCP server"""
        self.is_running = False
        if self.process:
            self.process.terminate()
            try:
                await asyncio.wait_for(self.process.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                self.process.kill()
                await self.process.wait()

# Global MCP manager
mcp_manager = MCPServerManager()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                self.disconnect(connection)

manager = ConnectionManager()

@app.on_event("startup")
async def startup_event():
    """Start MCP server on startup"""
    logger.info("Starting Telegram MCP Remote Server...")
    success = await mcp_manager.start_mcp_server()
    if not success:
        logger.error("Failed to start MCP server")
        # Don't exit, allow the web server to run for debugging
    else:
        logger.info("✅ Telegram MCP Server is ready!")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean shutdown"""
    logger.info("Shutting down...")
    await mcp_manager.stop()

# Health and info endpoints
@app.get("/")
async def root():
    """Root endpoint with server info"""
    return {
        "name": "Telegram MCP Remote Server",
        "version": "1.0.0",
        "description": "Remote access to local Telegram MCP server",
        "status": "running" if mcp_manager.is_running else "stopped",
        "endpoints": {
            "health": "/health",
            "tools": "/tools",
            "call": "/call/{tool_name}",
            "websocket": "/ws",