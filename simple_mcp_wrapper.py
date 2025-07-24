#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTTP Wrapper for existing MCP servers
Simple version for Windows compatibility
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

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "server": "mcp-http-wrapper",
        "timestamp": datetime.now().isoformat(),
        "message": "MCP server is running on port 8000"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "MCP HTTP Wrapper is running",
        "endpoints": {
            "health": "/health",
            "status": "/status"
        }
    }

@app.get("/status")
async def get_status():
    """Get server status"""
    return {
        "server_info": {
            "name": "mcp-http-wrapper",
            "version": "1.0.0",
            "type": "local-proxy",
            "port": 8000
        },
        "status": "ready"
    }

if __name__ == "__main__":
    print("Starting MCP HTTP Wrapper...")
    print("Server will run on: http://localhost:8000")
    print("Health check: http://localhost:8000/health")
    print("Press Ctrl+C to stop")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
