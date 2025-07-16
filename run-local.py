#!/usr/bin/env python3
"""
Local development runner for LinkedIn Agent
Provides an easy way to run the project locally without Docker for better performance
"""
import os
import sys
import subprocess
import threading
import time
from pathlib import Path

def run_backend():
    """Run the backend server"""
    print("🚀 Starting backend server...")
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    
    # Set environment variables for local development
    env = os.environ.copy()
    env.update({
        "REDIS_URL": "redis://localhost:6379/0",
        "SQLITE_PATH": str(Path(__file__).parent / "storage" / "data" / "jobs.db"),
        "JOBS_DIR": str(Path(__file__).parent / "storage" / "data" / "jobs"),
        "PYTHONUNBUFFERED": "1",
        "LOG_LEVEL": "INFO"
    })
    
    try:
        subprocess.run([sys.executable, "-m", "uvicorn", "src.server:app", "--reload", "--host", "0.0.0.0", "--port", "8000"], env=env)
    except KeyboardInterrupt:
        print("\n👋 Backend server stopped")

def run_frontend():
    """Run the frontend development server"""
    print("🎨 Starting frontend development server...")
    frontend_dir = Path(__file__).parent / "frontend"
    os.chdir(frontend_dir)
    
    try:
        subprocess.run(["npm", "run", "dev"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Frontend server stopped")

def check_prerequisites():
    """Check if required tools are available"""
    issues = []
    
    # Check Python
    try:
        result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
        print(f"✅ Python: {result.stdout.strip()}")
    except:
        issues.append("Python not found")
    
    # Check Node.js
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        print(f"✅ Node.js: {result.stdout.strip()}")
    except:
        issues.append("Node.js not found")
    
    # Check npm
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
        print(f"✅ npm: {result.stdout.strip()}")
    except:
        issues.append("npm not found")
    
    # Check if dependencies are installed
    backend_deps = Path(__file__).parent / "backend" / "src"
    if not backend_deps.exists():
        issues.append("Backend source not found")
    
    frontend_deps = Path(__file__).parent / "frontend" / "node_modules"
    if not frontend_deps.exists():
        issues.append("Frontend dependencies not installed (run: cd frontend && npm install)")
    
    return issues

def setup_storage():
    """Create necessary storage directories"""
    storage_dir = Path(__file__).parent / "storage" / "data"
    storage_dir.mkdir(parents=True, exist_ok=True)
    
    jobs_dir = storage_dir / "jobs"
    jobs_dir.mkdir(exist_ok=True)
    
    logs_dir = storage_dir / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    print(f"📁 Storage directories created at: {storage_dir}")

def main():
    """Main entry point"""
    print("🔍 LinkedIn Agent - Local Development Runner")
    print("=" * 50)
    
    # Check prerequisites
    issues = check_prerequisites()
    if issues:
        print("\n❌ Prerequisites missing:")
        for issue in issues:
            print(f"   - {issue}")
        print("\nPlease fix these issues before running.")
        return 1
    
    # Setup storage
    setup_storage()
    
    # Get command line argument
    mode = sys.argv[1] if len(sys.argv) > 1 else "fullstack"
    
    if mode == "backend":
        run_backend()
    elif mode == "frontend":
        run_frontend()
    elif mode == "fullstack":
        print("\n🚀 Starting full-stack development environment...")
        print("📡 Backend API will be available at: http://localhost:8000")
        print("🎨 Frontend will be available at: http://localhost:5173")
        print("🔧 API docs will be available at: http://localhost:8000/docs")
        print("\nPress Ctrl+C to stop all services\n")
        
        # Start backend in a separate thread
        backend_thread = threading.Thread(target=run_backend)
        backend_thread.daemon = True
        backend_thread.start()
        
        # Wait a moment for backend to start
        time.sleep(2)
        
        # Start frontend (this will block)
        try:
            run_frontend()
        except KeyboardInterrupt:
            print("\n👋 Shutting down all services...")
    else:
        print(f"Unknown mode: {mode}")
        print("Usage: python run-local.py [backend|frontend|fullstack]")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())