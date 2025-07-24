#!/usr/bin/env python3
"""
Test script for remote MCP access
Tests both local and Tailscale access
"""

import requests
import json
import time
import subprocess
import sys

def get_tailscale_ip():
    """Get Tailscale IP address"""
    try:
        result = subprocess.run(
            ["tailscale", "ip", "-4"], 
            capture_output=True, 
            text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return None
    except Exception as e:
        print(f"Error getting Tailscale IP: {e}")
        return None

def test_endpoint(url, endpoint, description):
    """Test a specific endpoint"""
    try:
        response = requests.get(f"{url}/{endpoint}", timeout=10)
        if response.status_code == 200:
            print(f"✅ {description}: OK")
            if endpoint == "health":
                data = response.json()
                print(f"   Status: {data.get('status')}")
                print(f"   MCP Server: {data.get('mcp_server_running')}")
            return True
        else:
            print(f"❌ {description}: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {description}: {e}")
        return False

def test_server(base_url, name):
    """Test all endpoints of a server"""
    print(f"\n🧪 Testing {name}: {base_url}")
    print("-" * 50)
    
    endpoints = [
        ("health", "Health Check"),
        ("mcp-manifest.json", "MCP Manifest"),
        ("status", "Server Status")
    ]
    
    success_count = 0
    for endpoint, description in endpoints:
        if test_endpoint(base_url, endpoint, description):
            success_count += 1
        time.sleep(0.5)
    
    if success_count == len(endpoints):
        print(f"🎉 {name} is fully operational!")
        return True
    else:
        print(f"⚠️  {name} has {len(endpoints) - success_count} failed tests")
        return False

def main():
    print("🚀 Testing Remote MCP Setup")
    print("=" * 50)
    
    # Test 1: Local access
    local_success = test_server("http://localhost:8000", "Local MCP Server")
    
    # Test 2: Tailscale access
    tailscale_ip = get_tailscale_ip()
    if tailscale_ip:
        tailscale_url = f"http://{tailscale_ip}:8000"
        tailscale_success = test_server(tailscale_url, "Tailscale Remote Access")
        
        if tailscale_success:
            print(f"\n🌐 Your remote MCP URL for Claude:")
            print(f"   {tailscale_url}")
            print(f"\n📱 Add this URL to Claude mobile settings!")
        
    else:
        print("\n⚠️  Tailscale not available or not connected")
        print("   Run: tailscale up")
        tailscale_success = False
    
    # Summary
    print(f"\n📊 Test Results:")
    print(f"   Local Server: {'✅' if local_success else '❌'}")
    print(f"   Remote Access: {'✅' if tailscale_success else '❌'}")
    
    if local_success and tailscale_success:
        print(f"\n🎉 Everything is working! Ready for Claude mobile!")
    elif local_success:
        print(f"\n⚠️  Local server works, set up Tailscale for remote access")
    else:
        print(f"\n❌ Local server issues - check if wrapper is running")

if __name__ == "__main__":
    main()