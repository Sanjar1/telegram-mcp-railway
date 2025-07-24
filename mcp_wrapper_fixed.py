#!/usr/bin/env python3
"""
HTTP Wrapper for existing MCP servers
This runs alongside your existing telegram-mcp and exposes it via HTTP/SSE
"""

import asyncio
import json
import logging
import subprocess
import sys
from typing import Any, Dict, List, Optional
from datetime import datetime
import os

from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(title="MCP HTTP Wrapper")

# CORS for Claude access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
mcp_connections: Dict[str, Any] = {}
mcp_process = None

class MCPServerManager:
    """Manages the MCP server process"""
    
    def __init__(self):
        self.process = None
        self.stdin = None
        self.stdout = None
        self.stderr = None
    
    async def start_mcp_server(self):
        """Start the existing MCP server"""
        try:
            # Command from your claude config
            cmd = [
                "uv", 
                "--directory", 
                r"C:\Users\99893\Downloads\mycode\telegram-mcp",
                "run",
                "main.py"
            ]
            
            logger.info(f"Starting MCP server: {' '.join(cmd)}")
            
            self.process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=r"C:\Users\99893\Downloads\mycode\telegram-mcp"
            )
            
            self.stdin = self.process.stdin
            self.stdout = self.process.stdout
            self.stderr = self.process.stderr
            
            logger.info("MCP server started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start MCP server: {e}")
            return False
    
    async def send_message(self, message: Dict) -> Dict:
        """Send message to MCP server and get response"""
        if not self.process or not self.stdin:
            raise Exception("MCP server not running")
        
        try:
            # Send message
            message_str = json.dumps(message) + "\n"
            self.stdin.write(message_str.encode())
            await self.stdin.drain()
            
            # Read response
            response_line = await self.stdout.readline()
            if response_line:
                response = json.loads(response_line.decode().strip())
                return response
            else:
                raise Exception("No response from MCP server")
                
        except Exception as e:
            logger.error(f"Error communicating with MCP server: {e}")
            raise
    
    async def stop(self):
        """Stop the MCP server"""
        if self.process:
            self.process.terminate()
            await self.process.wait()

# Global MCP manager
mcp_manager = MCPServerManager()

@app.on_event("startup")
async def startup_event():
    """Start MCP server on startup"""
    success = await mcp_manager.start_mcp_server()
    if not success:
        logger.error("Failed to start MCP server")
        sys.exit(1)

@app.on_event("shutdown")
async def shutdown_event():
    """Clean shutdown"""
    await mcp_manager.stop()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "server": "mcp-http-wrapper",
        "timestamp": datetime.now().isoformat(),
        "mcp_server_running": mcp_manager.process is not None
    }

@app.get("/mcp-manifest.json")
async def get_manifest():
    """MCP server manifest for Claude integration"""
    return {
        "version": "2025-03-26",
        "vendor": "local-mcp",
        "name": "telegram-mcp-remote",
        "description": "Remote access to local telegram-mcp server",
        "endpoints": {
            "sse": "/sse"
        },
        "auth": {
            "type": "none"
        }
    }

@app.get("/sse")
async def sse_endpoint(request: Request):
    """Server-Sent Events endpoint for Claude MCP communication"""
    
    async def event_stream():
        connection_id = f"conn_{datetime.now().timestamp()}"
        
        try:
            # Store connection
            mcp_connections[connection_id] = {
                "request": request,
                "connected_at": datetime.now()
            }
            
            logger.info(f"New SSE connection: {connection_id}")
            
            # Send initial connection event
            yield f"data: {json.dumps({'type': 'connection', 'id': connection_id})}\n\n"
            
            # Get tools list from MCP server
            try:
                tools_response = await mcp_manager.send_message({
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/list"
                })
                
                if "result" in tools_response:
                    yield f"data: {json.dumps({'type': 'tools', 'tools': tools_response['result']['tools']})}\n\n"
                
            except Exception as e:
                logger.error(f"Error getting tools: {e}")
            
            # Keep connection alive
            while True:
                if await request.is_disconnected():
                    break
                
                # Send heartbeat every 30 seconds
                yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': datetime.now().isoformat()})}\n\n"
                await asyncio.sleep(30)
                
        except Exception as e:
            logger.error(f"SSE connection error: {e}")
        finally:
            # Clean up connection
            if connection_id in mcp_connections:
                del mcp_connections[connection_id]
                logger.info(f"SSE connection closed: {connection_id}")
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )

@app.post("/sse")
async def handle_mcp_message(request: Request):
    """Handle incoming MCP messages from Claude"""
    try:
        body = await request.json()
        logger.info(f"Received MCP message: {body}")
        
        # Forward to local MCP server
        response = await mcp_manager.send_message(body)
        logger.info(f"MCP response: {response}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing MCP message: {e}")
        return {
            "jsonrpc": "2.0",
            "id": body.get("id") if 'body' in locals() else None,
            "error": {
                "code": -1,
                "message": str(e)
            }
        }

@app.get("/status")
async def get_status():
    """Get server status"""
    return {
        "active_connections": len(mcp_connections),
        "mcp_server_running": mcp_manager.process is not None,
        "mcp_server_pid": mcp_manager.process.pid if mcp_manager.process else None,
        "server_info": {
            "name": "mcp-http-wrapper",
            "version": "1.0.0",
            "type": "local-proxy"
        }
    }

if __name__ == "__main__":
    print("🚀 Starting MCP HTTP Wrapper...")
    print("📱 This exposes your local MCP servers for remote Claude access!")
    print("🔗 Server will run on: http://localhost:8000")
    print("📋 Health check: http://localhost:8000/health")
    print("📄 Manifest: http://localhost:8000/mcp-manifest.json")
    print("⚡ Your telegram-mcp will be accessible remotely!")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
