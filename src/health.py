"""
Health check module for monitoring system components.
Provides comprehensive health status for all dependencies.
"""

import os
import sqlite3
import redis
import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from pathlib import Path

logger = logging.getLogger(__name__)
router = APIRouter()

class HealthChecker:
    """Comprehensive health checker for all system components."""
    
    def __init__(self):
        self.redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
        self.sqlite_path = os.environ.get("SQLITE_PATH", "/app/data/jobs.db")
        self.jobs_dir = os.environ.get("JOBS_DIR", "/app/data/jobs")
    
    async def check_database(self) -> Dict[str, Any]:
        """Check SQLite database health."""
        try:
            conn = sqlite3.connect(self.sqlite_path)
            cursor = conn.cursor()
            
            # Check basic connectivity
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
            # Check table structure
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            # Check job statistics
            cursor.execute("SELECT COUNT(*) FROM jobs")
            total_jobs = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM jobs WHERE status='running'")
            running_jobs = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                "status": "healthy",
                "tables": tables,
                "total_jobs": total_jobs,
                "running_jobs": running_jobs,
                "path": self.sqlite_path
            }
            
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "path": self.sqlite_path
            }
    
    async def check_redis(self) -> Dict[str, Any]:
        """Check Redis connection and queue health."""
        try:
            r = redis.from_url(self.redis_url)
            
            # Test basic connectivity
            r.ping()
            
            # Check queue length
            queue_length = r.llen("job_queue")
            
            # Check Redis info
            info = r.info()
            
            return {
                "status": "healthy",
                "queue_length": queue_length,
                "redis_version": info.get("redis_version"),
                "connected_clients": info.get("connected_clients"),
                "used_memory_human": info.get("used_memory_human"),
                "url": self.redis_url
            }
            
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "url": self.redis_url
            }
    
    async def check_storage(self) -> Dict[str, Any]:
        """Check file storage health."""
        try:
            jobs_path = Path(self.jobs_dir)
            
            if not jobs_path.exists():
                return {
                    "status": "unhealthy",
                    "error": f"Jobs directory does not exist: {self.jobs_dir}"
                }
            
            if not os.access(jobs_path, os.W_OK):
                return {
                    "status": "unhealthy", 
                    "error": f"No write access to jobs directory: {self.jobs_dir}"
                }
            
            # Check available disk space
            statvfs = os.statvfs(jobs_path)
            free_space_gb = (statvfs.f_frsize * statvfs.f_bavail) / (1024**3)
            
            # Count job directories
            job_dirs = [d for d in jobs_path.iterdir() if d.is_dir() and d.name.startswith("job_")]
            
            return {
                "status": "healthy",
                "path": str(jobs_path),
                "free_space_gb": round(free_space_gb, 2),
                "job_directories": len(job_dirs),
                "writable": True
            }
            
        except Exception as e:
            logger.error(f"Storage health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "path": self.jobs_dir
            }
    
    async def check_environment(self) -> Dict[str, Any]:
        """Check environment variables and configuration."""
        required_vars = [
            "OPENAI_API_KEY",
            "APIFY_TOKEN", 
            "SUPABASE_JWT_SECRET"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.environ.get(var):
                missing_vars.append(var)
        
        return {
            "status": "healthy" if not missing_vars else "degraded",
            "missing_variables": missing_vars,
            "python_version": os.sys.version,
            "environment": os.environ.get("ENVIRONMENT", "development")
        }

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Comprehensive health check endpoint."""
    checker = HealthChecker()
    
    # Run all health checks
    db_status = await checker.check_database()
    redis_status = await checker.check_redis()
    storage_status = await checker.check_storage()
    env_status = await checker.check_environment()
    
    # Determine overall status
    component_statuses = [db_status, redis_status, storage_status, env_status]
    unhealthy_components = [c for c in component_statuses if c["status"] == "unhealthy"]
    degraded_components = [c for c in component_statuses if c["status"] == "degraded"]
    
    if unhealthy_components:
        overall_status = "unhealthy"
        http_status = 503
    elif degraded_components:
        overall_status = "degraded"
        http_status = 200
    else:
        overall_status = "healthy"
        http_status = 200
    
    response = {
        "status": overall_status,
        "timestamp": os.environ.get("TIMESTAMP", "unknown"),
        "version": "1.0.0",
        "components": {
            "database": db_status,
            "redis": redis_status,
            "storage": storage_status,
            "environment": env_status
        }
    }
    
    # Set appropriate HTTP status code
    if http_status != 200:
        raise HTTPException(status_code=http_status, detail=response)
    
    return response

@router.get("/health/simple")
async def simple_health_check() -> Dict[str, str]:
    """Simple health check for load balancers."""
    return {"status": "ok"}

@router.get("/health/ready")
async def readiness_check() -> Dict[str, str]:
    """Readiness check for Kubernetes."""
    checker = HealthChecker()
    
    # Check critical components
    db_status = await checker.check_database()
    redis_status = await checker.check_redis()
    
    if db_status["status"] == "healthy" and redis_status["status"] == "healthy":
        return {"status": "ready"}
    else:
        raise HTTPException(status_code=503, detail="Service not ready")

@router.get("/health/live")
async def liveness_check() -> Dict[str, str]:
    """Liveness check for Kubernetes."""
    return {"status": "alive"}