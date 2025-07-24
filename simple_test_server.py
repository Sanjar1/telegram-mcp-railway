#!/usr/bin/env python3
# Simple test server to verify HTTP wrapper works
# Run this first to test basic functionality

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime

app = FastAPI(title="Simple MCP Test Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "server": "simple-test",
        "timestamp": datetime.now().isoformat(),
        "message": "HTTP wrapper is working!"
    }

@app.get("/mcp-manifest.json")
async def get_manifest():
    return {
        "version": "2025-03-26",
        "vendor": "test",
        "name": "simple-test",
        "description": "Simple test server",
        "endpoints": {
            "sse": "/sse"
        },
        "auth": {
            "type": "none"
        }
    }

@app.get("/status")
async def get_status():
    return {
        "server": "simple-test",
        "tailscale_ip": "100.116.173.65",
        "local_url": "http://localhost:8000",
        "remote_url": "http://100.116.173.65:8000",
        "ready_for_claude": True
    }

if __name__ == "__main__":
    print("🧪 Starting Simple Test Server...")
    print("🔗 Local: http://localhost:8000")
    print("🌐 Remote: http://100.116.173.65:8000")
    print("📋 Test: http://localhost:8000/health")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )