#!/usr/bin/env python3
"""
Startup script for Train Traffic Throughput Maximization System
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    print("🚂 Train Traffic Throughput Maximization System")
    print("=" * 60)
    print("🤖 Advanced AI-Powered Railway Optimization Platform")
    print("=" * 60)
    print()
    
    # Check if requirements are installed
    try:
        import fastapi
        import uvicorn
        print("✅ Dependencies are installed")
    except ImportError:
        print("❌ Installing dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed")
    
    print()
    print("🌐 Starting the application...")
    print("📱 Dashboard: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/api/docs")
    print("🔧 Health Check: http://localhost:8000/api/health")
    print()
    print("Press Ctrl+C to stop the application")
    print("=" * 60)
    
    # Start the application
    try:
        subprocess.run([sys.executable, "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
