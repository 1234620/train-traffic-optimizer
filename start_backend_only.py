#!/usr/bin/env python3
"""
Backend-only startup script for the Train Traffic Throughput Maximization System
Runs the FastAPI backend with static frontend serving
"""

import subprocess
import sys
import time
import signal

def check_requirements():
    """Check if Python requirements are installed"""
    print("🔍 Checking Python requirements...")
    
    try:
        import fastapi
        import uvicorn
        print("✅ Python backend dependencies found")
        return True
    except ImportError as e:
        print(f"❌ Missing Python dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def start_backend():
    """Start the FastAPI backend"""
    print("🚀 Starting backend server...")
    try:
        # Start the backend
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "app:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ])
        print("✅ Backend server started successfully!")
        return process
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return None

def main():
    """Main startup function"""
    print("🚂 Train Traffic Throughput Maximization System")
    print("🔧 Backend-Only Mode")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Requirements check failed. Please install missing dependencies.")
        sys.exit(1)
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        print("\n❌ Failed to start backend.")
        sys.exit(1)
    
    print("\n🎉 Backend started successfully!")
    print("=" * 50)
    print("🌐 Frontend: http://localhost:8000")
    print("🔧 Backend API: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/api/docs")
    print("🔌 WebSocket: ws://localhost:8000/ws")
    print("=" * 50)
    print("Press Ctrl+C to stop the server")
    
    try:
        while True:
            time.sleep(1)
            if backend_process.poll() is not None:
                print("\n❌ Backend process stopped unexpectedly")
                break
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        backend_process.terminate()
        print("✅ Backend stopped")
        print("👋 System shutdown complete")

if __name__ == "__main__":
    main()
