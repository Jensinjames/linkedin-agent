"""
Simple local adapter that removes external dependencies.
Uses file-based authentication and local storage only.
"""
import json
import hashlib
from datetime import datetime
from pathlib import Path
from .base import PlatformAdapter

class SimpleLocalAdapter(PlatformAdapter):
    def __init__(self, data_dir: str = "/app/data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.users_file = self.data_dir / "users.json"
        self.jobs_dir = self.data_dir / "jobs"
        self.jobs_dir.mkdir(exist_ok=True)
        
    async def get_input(self):
        """Get input from file or stdin - no external API needed"""
        import sys
        if len(sys.argv) > 1:
            safe_root = self.data_dir  # Define a safe root directory
            user_path = Path(sys.argv[1])
            normalized_path = user_path.resolve()
            if not normalized_path.is_relative_to(safe_root):
                raise ValueError("Access to the specified path is not allowed.")
            with open(normalized_path) as f:
                return json.load(f)
        else:
            return json.load(sys.stdin)
    
    async def push_data(self, data):
        """Save data locally instead of to external platform"""
        timestamp = datetime.now().isoformat()
        job_id = hashlib.md5(str(data).encode()).hexdigest()[:8]
        
        output_file = self.jobs_dir / f"job_{job_id}_{timestamp}.json"
        with open(output_file, 'w') as f:
            json.dump({
                "job_id": job_id,
                "timestamp": timestamp,
                "data": data
            }, f, indent=2)
        
        print(f"Results saved to: {output_file}")
        return job_id
    
    def log_info(self, msg):
        """Simple logging to console and file"""
        timestamp = datetime.now().isoformat()
        log_msg = f"[{timestamp}] {msg}"
        print(log_msg)
        
        # Also log to file
        log_file = self.data_dir / "app.log"
        with open(log_file, 'a') as f:
            f.write(log_msg + "\n")
    
    async def fail(self, status_message, exception=None):
        """Handle failures locally"""
        error_data = {
            "status": "failed",
            "message": status_message,
            "timestamp": datetime.now().isoformat(),
            "error": str(exception) if exception else None
        }
        
        error_file = self.data_dir / "errors.json"
        errors = []
        if error_file.exists():
            with open(error_file) as f:
                errors = json.load(f)
        
        errors.append(error_data)
        with open(error_file, 'w') as f:
            json.dump(errors, f, indent=2)
        
        self.log_info(f"Error logged: {status_message}")
        raise Exception(status_message)
    
    def create_user(self, username: str, password: str, is_admin: bool = False):
        """Create a simple local user account"""
        users = self.get_users()
        
        # Hash password (simple approach - use proper hashing in production)
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        users[username] = {
            "password_hash": password_hash,
            "is_admin": is_admin,
            "created_at": datetime.now().isoformat()
        }
        
        self.save_users(users)
        return True
    
    def authenticate_user(self, username: str, password: str):
        """Simple local authentication"""
        users = self.get_users()
        if username not in users:
            return None
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if users[username]["password_hash"] == password_hash:
            return {
                "username": username,
                "is_admin": users[username]["is_admin"]
            }
        return None
    
    def get_users(self):
        """Get users from local file"""
        if self.users_file.exists():
            with open(self.users_file) as f:
                return json.load(f)
        return {}
    
    def save_users(self, users):
        """Save users to local file"""
        with open(self.users_file, 'w') as f:
            json.dump(users, f, indent=2)
