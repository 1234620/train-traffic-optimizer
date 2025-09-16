#!/usr/bin/env python3
"""
Windows-optimized startup script for the Train Traffic Throughput Maximization System
Handles common Windows issues with Node.js and npm
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
        result = subprocess.run(["node", "--version"], capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            print(f"✅ Node.js found: {result.stdout.strip()}")
        else:
            print("❌ Node.js not found")
            return False
    except FileNotFoundError:
        print("❌ Node.js not found")
        return False
    
    # Check if npm is available
    npm_found = False
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            print(f"✅ npm found: {result.stdout.strip()}")
            npm_found = True
        else:
            print("⚠️ npm not found in PATH, trying alternative methods...")
    except FileNotFoundError:
        print("⚠️ npm not found in PATH, trying alternative methods...")
    
    # Try to find npm in common locations
    if not npm_found:
        common_npm_paths = [
            r"C:\Program Files\nodejs\npm.cmd",
            r"C:\Program Files (x86)\nodejs\npm.cmd",
            os.path.expanduser(r"~\AppData\Roaming\npm\npm.cmd"),
            os.path.expanduser(r"~\AppData\Local\npm\npm.cmd")
        ]
        
        for npm_path in common_npm_paths:
            if os.path.exists(npm_path):
                print(f"✅ Found npm at: {npm_path}")
                # Add to PATH for this session
                os.environ["PATH"] = os.path.dirname(npm_path) + os.pathsep + os.environ["PATH"]
                npm_found = True
                break
    
    if not npm_found:
        print("❌ npm not found. Please install Node.js with npm or use the backend-only mode.")
        print("You can:")
        print("1. Install Node.js from https://nodejs.org/ (includes npm)")
        print("2. Run backend only: python app.py")
        print("3. Use the pre-built frontend if available")
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
                text=True,
                shell=True
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
                text=True,
                shell=True
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
            cwd=frontend_dir,
            shell=True
        )
        print("✅ Frontend development server started on http://localhost:3000")
        return process
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return None

def start_backend_only():
    """Start only the backend with static frontend serving"""
    print("🚀 Starting backend with static frontend...")
    try:
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "app:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ])
        print("✅ Backend server started on http://localhost:8000")
        print("📱 Frontend will be served from the backend at http://localhost:8000")
        return process
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return None

def main():
    """Main startup function"""
    print("🚂 Train Traffic Throughput Maximization System")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        print("\n🔄 Trying backend-only mode...")
        backend_process = start_backend_only()
        if backend_process:
            print("\n🎉 Backend started successfully!")
            print("=" * 50)
            print("🌐 Frontend: http://localhost:8000")
            print("🔧 Backend API: http://localhost:8000")
            print("📚 API Docs: http://localhost:8000/api/docs")
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
        return
    
    # Install frontend dependencies
    if not install_frontend_dependencies():
        print("\n🔄 Trying backend-only mode...")
        backend_process = start_backend_only()
        if backend_process:
            print("\n🎉 Backend started successfully!")
            print("=" * 50)
            print("🌐 Frontend: http://localhost:8000")
            print("🔧 Backend API: http://localhost:8000")
            print("📚 API Docs: http://localhost:8000/api/docs")
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
        return
    
    # Build frontend
    if not build_frontend():
        print("\n🔄 Trying backend-only mode...")
        backend_process = start_backend_only()
        if backend_process:
            print("\n🎉 Backend started successfully!")
            print("=" * 50)
            print("🌐 Frontend: http://localhost:8000")
            print("🔧 Backend API: http://localhost:8000")
            print("📚 API Docs: http://localhost:8000/api/docs")
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
        return
    
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
        print("\n⚠️ Frontend failed to start, but backend is running")
        print("🌐 Access the system at: http://localhost:8000")
        print("Press Ctrl+C to stop the backend")
        
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
        return
    
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
