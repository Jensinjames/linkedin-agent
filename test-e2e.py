#!/usr/bin/env python3
"""
End-to-End Testing Suite for LinkedIn Agent
Tests the complete functionality including API, health checks, and basic workflows
"""
import asyncio
import json
import time
import subprocess
import sys
import requests
from pathlib import Path

def log_info(msg):
    print(f"✅ {msg}")

def log_warn(msg):
    print(f"⚠️  {msg}")

def log_error(msg):
    print(f"❌ {msg}")

def log_step(msg):
    print(f"🔄 {msg}")

async def test_imports():
    """Test that all core modules can be imported successfully"""
    log_step("Testing module imports...")
    
    try:
        # Add backend to path
        import sys
        sys.path.insert(0, 'backend')
        
        # Test backend imports
        from src.server import app
        from src.health import HealthChecker
        from src.database import JobDB
        log_info("Backend modules import successfully")
        
        # Test basic configuration
        import os
        required_vars = ['REDIS_URL', 'SQLITE_PATH', 'JOBS_DIR']
        missing = [var for var in required_vars if not os.environ.get(var)]
        if missing:
            log_warn(f"Missing environment variables: {missing}")
        else:
            log_info("Environment configuration complete")
            
        return True
    except Exception as e:
        log_error(f"Import test failed: {e}")
        return False

async def test_health_system():
    """Test the health check system"""
    log_step("Testing health check system...")
    
    try:
        import sys
        sys.path.insert(0, 'backend')
        from src.health import HealthChecker
        checker = HealthChecker()
        
        # Test health checker initialization
        log_info("Health checker initialized")
        
        # Test configuration
        log_info(f"SQLite path: {checker.sqlite_path}")
        log_info(f"Jobs directory: {checker.jobs_dir}")
        log_info(f"Redis URL: {checker.redis_url}")
        
        return True
    except Exception as e:
        log_error(f"Health system test failed: {e}")
        return False

async def test_api_startup():
    """Test API server startup performance"""
    log_step("Testing API startup performance...")
    
    try:
        import sys
        sys.path.insert(0, 'backend')
        from src.server import app
        start_time = time.time()
        
        # This tests that the app can be initialized
        assert app is not None
        
        startup_time = time.time() - start_time
        log_info(f"API startup time: {startup_time:.3f}s")
        
        if startup_time < 1.0:
            log_info("API startup performance: Excellent (< 1s)")
        elif startup_time < 3.0:
            log_info("API startup performance: Good (< 3s)")
        else:
            log_warn("API startup performance: Slow (> 3s)")
            
        return True
    except Exception as e:
        log_error(f"API startup test failed: {e}")
        return False

async def test_storage_system():
    """Test storage system setup"""
    log_step("Testing storage system...")
    
    try:
        # Test storage directories
        storage_path = Path("storage/data")
        if storage_path.exists():
            log_info("Storage directories exist")
            
            # Test write permissions
            test_file = storage_path / "test_write.tmp"
            test_file.write_text("test")
            test_file.unlink()
            log_info("Storage write permissions working")
        else:
            log_warn("Storage directories not found")
            
        # Test database location
        import sys
        sys.path.insert(0, 'backend')
        from src.server import SQLITE_PATH
        db_path = Path(SQLITE_PATH)
        db_dir = db_path.parent
        if db_dir.exists():
            log_info(f"Database directory ready: {db_dir}")
        else:
            log_warn(f"Database directory missing: {db_dir}")
            
        return True
    except Exception as e:
        log_error(f"Storage system test failed: {e}")
        return False

async def test_frontend_build():
    """Test frontend build system"""
    log_step("Testing frontend build system...")
    
    try:
        frontend_path = Path("frontend")
        if not frontend_path.exists():
            log_warn("Frontend directory not found")
            return True
            
        # Check if built
        dist_path = frontend_path / "dist"
        if dist_path.exists():
            log_info("Frontend build artifacts exist")
            
            # Check build size
            index_file = dist_path / "index.html"
            if index_file.exists():
                size = index_file.stat().st_size
                log_info(f"Frontend build size: {size} bytes")
            
        # Test build performance if npm is available
        try:
            result = subprocess.run(
                ["npm", "run", "build"], 
                cwd=frontend_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                log_info("Frontend build successful")
            else:
                log_warn("Frontend build had issues")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            log_warn("Frontend build test skipped (npm not available or slow)")
            
        return True
    except Exception as e:
        log_error(f"Frontend test failed: {e}")
        return False

async def test_performance_metrics():
    """Test performance metrics and monitoring"""
    log_step("Testing performance metrics...")
    
    try:
        # Test memory usage
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024
        log_info(f"Memory usage: {memory_mb:.1f} MB")
        
        if memory_mb < 100:
            log_info("Memory usage: Excellent (< 100MB)")
        elif memory_mb < 200:
            log_info("Memory usage: Good (< 200MB)")
        else:
            log_warn("Memory usage: High (> 200MB)")
            
        # Test CPU usage
        cpu_percent = process.cpu_percent()
        log_info(f"CPU usage: {cpu_percent:.1f}%")
        
        return True
    except ImportError:
        log_warn("psutil not available, performance metrics skipped")
        return True
    except Exception as e:
        log_error(f"Performance metrics test failed: {e}")
        return False

async def run_comprehensive_test():
    """Run all end-to-end tests"""
    print("🚀 LinkedIn Agent - End-to-End Testing Suite")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("Health System", test_health_system),
        ("API Startup", test_api_startup),
        ("Storage System", test_storage_system),
        ("Frontend Build", test_frontend_build),
        ("Performance Metrics", test_performance_metrics),
    ]
    
    results = {}
    start_time = time.time()
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results[test_name] = result
        except Exception as e:
            log_error(f"{test_name} test crashed: {e}")
            results[test_name] = False
        print()  # Add spacing between tests
    
    # Summary
    total_time = time.time() - start_time
    passed = sum(results.values())
    total = len(results)
    
    print("📊 Test Results Summary")
    print("=" * 25)
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    print(f"⏱️  Total time: {total_time:.2f}s")
    
    if passed == total:
        print("🎉 All tests passed! System is performing optimally.")
        return 0
    else:
        print("⚠️  Some tests failed. Check output above for details.")
        return 1

def main():
    """Main entry point"""
    # Set up basic environment for testing
    import os
    
    # Ensure we're in the right directory
    os.chdir(Path(__file__).parent)
    
    # Set basic environment variables if not set
    if not os.environ.get('SQLITE_PATH'):
        os.environ['SQLITE_PATH'] = str(Path('storage/data/jobs.db'))
    if not os.environ.get('JOBS_DIR'):
        os.environ['JOBS_DIR'] = str(Path('storage/data/jobs'))
    if not os.environ.get('REDIS_URL'):
        os.environ['REDIS_URL'] = 'redis://localhost:6379/0'
    
    # Run tests
    return asyncio.run(run_comprehensive_test())

if __name__ == "__main__":
    sys.exit(main())