#!/usr/bin/env python3
"""
Startup script for the complete Train Traffic Throughput Maximization System
Runs both backend (FastAPI) and frontend (Next.js) simultaneously
"""

import subprocess
import sys
import os
import time
import signal
import threading
from pathlib import Path

def check_requirements():
    """Check if all requirements are installed"""
    print("🔍 Checking requirements...")
    
    # Check Python packages
    try:
        import fastapi
        import uvicorn
        print("✅ Python backend dependencies found")
    except ImportError as e:
        print(f"❌ Missing Python dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False
    
    # Check if Node.js is available
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js found: {result.stdout.strip()}")
        else:
            print("❌ Node.js not found")
            return False
    except FileNotFoundError:
        print("❌ Node.js not found")
        return False
    
    # Check if npm is available
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ npm found: {result.stdout.strip()}")
        else:
            print("❌ npm not found")
            return False
    except FileNotFoundError:
        print("❌ npm not found")
        return False
    
    return True

def install_frontend_dependencies():
    """Install frontend dependencies if needed"""
    frontend_dir = Path("railway-optimization")
    node_modules = frontend_dir / "node_modules"
    
    if not node_modules.exists():
        print("📦 Installing frontend dependencies...")
        try:
            result = subprocess.run(
                ["npm", "install"],
                cwd=frontend_dir,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print("✅ Frontend dependencies installed")
            else:
                print(f"❌ Failed to install frontend dependencies: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Error installing frontend dependencies: {e}")
            return False
    else:
        print("✅ Frontend dependencies already installed")
    
    return True

def build_frontend():
    """Build the frontend for production"""
    frontend_dir = Path("railway-optimization")
    out_dir = frontend_dir / "out"
    
    if not out_dir.exists():
        print("🏗️ Building frontend...")
        try:
            result = subprocess.run(
                ["npm", "run", "build"],
                cwd=frontend_dir,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print("✅ Frontend built successfully")
            else:
                print(f"❌ Failed to build frontend: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Error building frontend: {e}")
            return False
    else:
        print("✅ Frontend already built")
    
    return True

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
        print("✅ Backend server started on http://localhost:8000")
        return process
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return None

def start_frontend_dev():
    """Start the Next.js frontend in development mode"""
    print("🎨 Starting frontend development server...")
    try:
        frontend_dir = Path("railway-optimization")
        process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=frontend_dir
        )
        print("✅ Frontend development server started on http://localhost:3000")
        return process
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return None

def main():
    """Main startup function"""
    print("🚂 Train Traffic Throughput Maximization System")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Requirements check failed. Please install missing dependencies.")
        sys.exit(1)
    
    # Install frontend dependencies
    if not install_frontend_dependencies():
        print("\n❌ Failed to install frontend dependencies.")
        sys.exit(1)
    
    # Build frontend
    if not build_frontend():
        print("\n❌ Failed to build frontend.")
        sys.exit(1)
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        print("\n❌ Failed to start backend.")
        sys.exit(1)
    
    # Wait a moment for backend to start
    time.sleep(3)
    
    # Start frontend
    frontend_process = start_frontend_dev()
    if not frontend_process:
        print("\n❌ Failed to start frontend.")
        backend_process.terminate()
        sys.exit(1)
    
    print("\n🎉 System started successfully!")
    print("=" * 50)
    print("🌐 Frontend: http://localhost:3000")
    print("🔧 Backend API: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/api/docs")
    print("=" * 50)
    print("Press Ctrl+C to stop all services")
    
    try:
        # Wait for both processes
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if backend_process.poll() is not None:
                print("\n❌ Backend process stopped unexpectedly")
                break
            
            if frontend_process.poll() is not None:
                print("\n❌ Frontend process stopped unexpectedly")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")
        
        # Terminate processes
        if backend_process:
            backend_process.terminate()
            print("✅ Backend stopped")
        
        if frontend_process:
            frontend_process.terminate()
            print("✅ Frontend stopped")
        
        print("👋 System shutdown complete")

if __name__ == "__main__":
    main()
