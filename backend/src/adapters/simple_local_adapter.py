"""
Simple local adapter that removes external dependencies.
Uses file-based authentication and structured local storage.
"""
import json
import hashlib
from datetime import datetime
from pathlib import Path
from .base import PlatformAdapter
from ..storage_manager import JobStorageManager
from ..schemas_output import JobResult, JobMetadata, ContactInfo, JobStatus

class SimpleLocalAdapter(PlatformAdapter):
    def __init__(self, data_dir: str = "/app/data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.users_file = self.data_dir / "users.json"
        self.storage_manager = JobStorageManager(str(self.data_dir))
        
    async def get_input(self):
        """Get input from file or stdin - no external API needed"""
        import sys
        if len(sys.argv) > 1:
            safe_root = self.data_dir.resolve()  # Define a safe root directory
            user_path = Path(sys.argv[1])
            normalized_path = user_path.resolve()
            if not normalized_path.is_relative_to(safe_root):
                raise ValueError("Access to the specified path is not allowed.")
            with open(normalized_path) as f:
                return json.load(f)
        else:
            return json.load(sys.stdin)
    
    async def push_data(self, data, input_url: str = "unknown") -> str:
        """Save data using structured storage manager"""
        try:
            # Generate job ID
            job_id = self.storage_manager.generate_job_id(str(data))
            
            # Create job metadata
            created_at = datetime.now()
            metadata = JobMetadata(
                job_id=job_id,
                status=JobStatus.COMPLETED,
                created_at=created_at,
                completed_at=created_at,
                processing_time_seconds=0.0,  # Will be updated if timing is tracked
                input_url=input_url or "unknown",
                total_contacts=0,
                errors_count=0
            )
            
            # Parse contacts from data
            contacts = []
            if isinstance(data, dict):
                if 'contacts' in data:
                    # Data already has contacts structure
                    for contact_data in data.get('contacts', []):
                        contact = ContactInfo(**contact_data)
                        contacts.append(contact)
                else:
                    # Single contact data
                    contact = ContactInfo(
                        name=data.get('name'),
                        title=data.get('title'),
                        company=data.get('company'),
                        location=data.get('location'),
                        emails=data.get('emails', []),
                        phones=data.get('phones', []),
                        social_links=data.get('social_links', {}),
                        linkedin_url=data.get('linkedin_url'),
                        website=data.get('website'),
                        description=data.get('description')
                    )
                    contacts.append(contact)
            
            # Update metadata with actual counts
            metadata.total_contacts = len(contacts)
            
            # Create job result
            job_result = JobResult(
                metadata=metadata,
                contacts=contacts,
                errors=[],
                summary=data.get('summary'),
                raw_data=data if isinstance(data, dict) else None
            )
            
            # Save using storage manager
            storage_path = self.storage_manager.save_job_result(job_result)
            
            self.log_info(f"Results saved with job ID: {job_id}")
            self.log_info(f"Storage location: {storage_path}")
            self.log_info(f"Contacts found: {len(contacts)}")
            
            return job_id
            
        except Exception as e:
            self.log_info(f"Error saving job data: {str(e)}")
            # Fallback to simple save
            return await self._simple_push_data(data)
    
    async def _simple_push_data(self, data):
        """Fallback simple data save method"""
        timestamp = datetime.now().isoformat()
        job_id = hashlib.md5(str(data).encode()).hexdigest()[:8]
        
        jobs_dir = self.data_dir / "jobs"
        jobs_dir.mkdir(exist_ok=True)
        
        output_file = jobs_dir / f"job_{job_id}_{timestamp}.json"
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
