#!/usr/bin/env python3
"""
Development startup script for CashFlow Monitor.
This script starts both the backend and frontend development servers.
"""
import subprocess
import sys
import time
import os
from pathlib import Path


def print_banner():
    """Print application banner."""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                    🚀 CashFlow Monitor 🚀                    ║
    ║                                                              ║
    ║        Personal Finance Management with Open Finance        ║
    ║                    Brasil Integration                       ║
    ╚══════════════════════════════════════════════════════════════╝
    """)


def check_prerequisites():
    """Check if required tools are installed."""
    print("🔍 Checking prerequisites...")
    
    # Check Python version
    if sys.version_info < (3, 11):
        print("❌ Python 3.11+ is required")
        return False
    
    # Check if Poetry is installed
    try:
        subprocess.run(["poetry", "--version"], check=True, capture_output=True)
        print("✅ Poetry is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Poetry is not installed. Please install it first:")
        print("   curl -sSL https://install.python-poetry.org | python3 -")
        return False
    
    # Check if Node.js is installed
    try:
        subprocess.run(["node", "--version"], check=True, capture_output=True)
        print("✅ Node.js is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Node.js is not installed. Please install it first.")
        return False
    
    # Check if npm is installed
    try:
        subprocess.run(["npm", "--version"], check=True, capture_output=True)
        print("✅ npm is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ npm is not installed. Please install it first.")
        return False
    
    print("✅ All prerequisites are met!")
    return True


def setup_backend():
    """Setup and start the backend server."""
    print("\n🔧 Setting up backend...")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False
    
    # Install dependencies
    print("📦 Installing backend dependencies...")
    try:
        subprocess.run(["poetry", "install"], cwd=backend_dir, check=True)
        print("✅ Backend dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install backend dependencies: {e}")
        return False
    
    return True


def setup_frontend():
    """Setup and start the frontend server."""
    print("\n🎨 Setting up frontend...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    # Install dependencies
    print("📦 Installing frontend dependencies...")
    try:
        subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
        print("✅ Frontend dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install frontend dependencies: {e}")
        return False
    
    return True


def start_backend():
    """Start the backend server in a separate process."""
    print("\n🚀 Starting backend server...")
    
    backend_dir = Path("backend")
    try:
        # Start backend server
        backend_process = subprocess.Popen(
            ["poetry", "run", "uvicorn", "app.main:app", "--reload", "--host", "127.0.0.1", "--port", "8000"],
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait a bit for server to start
        time.sleep(3)
        
        if backend_process.poll() is None:
            print("✅ Backend server started at http://127.0.0.1:8000")
            return backend_process
        else:
            print("❌ Backend server failed to start")
            return None
            
    except Exception as e:
        print(f"❌ Failed to start backend server: {e}")
        return None


def start_frontend():
    """Start the frontend server in a separate process."""
    print("\n🌐 Starting frontend server...")
    
    frontend_dir = Path("frontend")
    try:
        # Start frontend server
        frontend_process = subprocess.Popen(
            ["npm", "start"],
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait a bit for server to start
        time.sleep(5)
        
        if frontend_process.poll() is None:
            print("✅ Frontend server started at http://localhost:3000")
            return frontend_process
        else:
            print("❌ Frontend server failed to start")
            return None
            
    except Exception as e:
        print(f"❌ Failed to start frontend server: {e}")
        return None


def main():
    """Main function to setup and start the development environment."""
    print_banner()
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites check failed. Please install required tools.")
        sys.exit(1)
    
    # Setup backend
    if not setup_backend():
        print("\n❌ Backend setup failed.")
        sys.exit(1)
    
    # Setup frontend
    if not setup_frontend():
        print("\n❌ Frontend setup failed.")
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Start backend: cd backend && poetry run dev")
    print("2. Start frontend: cd frontend && npm start")
    print("3. Open http://localhost:3000 in your browser")
    print("4. Backend API available at http://127.0.0.1:8000")
    print("5. API documentation at http://127.0.0.1:8000/docs")
    
    print("\n💡 Development Tips:")
    print("- Backend will auto-reload on code changes")
    print("- Frontend will auto-reload on code changes")
    print("- Check the terminal output for any errors")
    print("- Use Ctrl+C to stop the servers")
    
    print("\n🚀 Happy coding!")


if __name__ == "__main__":
    main()
