"""
Enhanced storage manager for LinkedIn Agent with structured output.
Handles automatic saving, formatting, and retrieval of job data.
"""
import json
import csv
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional
import logging

from .schemas_output import JobResult, JobMetadata, JobStatus

logger = logging.getLogger(__name__)

class JobStorageManager:
    """Manages structured storage of job results with multiple output formats"""
    
    def __init__(self, storage_dir: str = "../storage/data"):
        self.storage_dir = Path(storage_dir).resolve()
        self.jobs_dir = self.storage_dir / "jobs"
        self.logs_dir = self.storage_dir / "logs"
        self.exports_dir = self.storage_dir / "exports"
        
        # Create directories
        for dir_path in [self.storage_dir, self.jobs_dir, self.logs_dir, self.exports_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        self.log_file = self.logs_dir / "job_manager.log"
        
    def _log(self, message: str, level: str = "INFO"):
        """Internal logging with timestamp"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")
    
    def generate_job_id(self, input_data: str) -> str:
        """Generate a unique job ID based on input and timestamp"""
        timestamp = datetime.now().isoformat()
        combined = f"{input_data}_{timestamp}"
        return hashlib.md5(combined.encode()).hexdigest()[:12]
    
    def save_job_result(self, job_result: JobResult) -> str:
        """Save a complete job result with multiple formats"""
        job_id = job_result.metadata.job_id
        job_dir = self.jobs_dir / job_id
        job_dir.mkdir(exist_ok=True)
        
        try:
            # Save as JSON (structured)
            json_file = job_dir / "result.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(job_result.dict(), f, indent=2, default=str)
            
            # Save as formatted JSON (human-readable)
            formatted_file = job_dir / "result_formatted.json"
            with open(formatted_file, 'w', encoding='utf-8') as f:
                json.dump(job_result.to_formatted_dict(), f, indent=2, default=str)
            
            # Save as CSV
            csv_file = job_dir / "contacts.csv"
            csv_data = job_result.to_csv_data()
            if csv_data:
                with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=csv_data[0].keys())
                    writer.writeheader()
                    writer.writerows(csv_data)
            
            # Save summary text file
            summary_file = job_dir / "summary.txt"
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(self._generate_text_summary(job_result))
            
            # Save metadata
            metadata_file = job_dir / "metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(job_result.metadata.dict(), f, indent=2, default=str)
            
            self._log(f"Job {job_id} saved successfully to {job_dir}")
            return str(job_dir)
            
        except Exception as e:
            self._log(f"Failed to save job {job_id}: {str(e)}", "ERROR")
            raise
    
    def _generate_text_summary(self, job_result: JobResult) -> str:
        """Generate a human-readable text summary"""
        summary_lines = [
            "=" * 60,
            "LinkedIn Agent Job Report",
            "=" * 60,
            f"Job ID: {job_result.metadata.job_id}",
            f"Status: {job_result.metadata.status.value.upper()}",
            f"Input URL: {job_result.metadata.input_url}",
            f"Created: {job_result.metadata.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
        ]
        
        if job_result.metadata.completed_at:
            summary_lines.append(f"Completed: {job_result.metadata.completed_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if job_result.metadata.processing_time_seconds:
            summary_lines.append(f"Processing Time: {job_result.metadata.processing_time_seconds:.2f} seconds")
        
        summary_lines.extend([
            "",
            "RESULTS SUMMARY:",
            "-" * 30,
            f"Total Contacts Found: {len(job_result.contacts)}",
            f"Contacts with Emails: {len([c for c in job_result.contacts if c.emails])}",
            f"Contacts with Phones: {len([c for c in job_result.contacts if c.phones])}",
            f"Social Links Found: {sum(len(c.social_links) for c in job_result.contacts)}",
            f"Errors Encountered: {len(job_result.errors)}",
        ])
        
        if job_result.contacts:
            summary_lines.extend([
                "",
                "CONTACT DETAILS:",
                "-" * 30
            ])
            
            for i, contact in enumerate(job_result.contacts[:5], 1):  # Show first 5 contacts
                summary_lines.append(f"\n{i}. {contact.name or 'Unknown Name'}")
                if contact.title:
                    summary_lines.append(f"   Title: {contact.title}")
                if contact.company:
                    summary_lines.append(f"   Company: {contact.company}")
                if contact.emails:
                    summary_lines.append(f"   Emails: {', '.join(contact.emails)}")
                if contact.phones:
                    summary_lines.append(f"   Phones: {', '.join(contact.phones)}")
                if contact.linkedin_url:
                    summary_lines.append(f"   LinkedIn: {contact.linkedin_url}")
            
            if len(job_result.contacts) > 5:
                summary_lines.append(f"\n... and {len(job_result.contacts) - 5} more contacts")
        
        if job_result.errors:
            summary_lines.extend([
                "",
                "ERRORS:",
                "-" * 30
            ])
            for error in job_result.errors:
                summary_lines.append(f"• {error.error_message}")
        
        if job_result.summary:
            summary_lines.extend([
                "",
                "AI SUMMARY:",
                "-" * 30,
                job_result.summary
            ])
        
        summary_lines.extend([
            "",
            "=" * 60,
            f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 60
        ])
        
        return "\n".join(summary_lines)
    
    def load_job_result(self, job_id: str) -> Optional[JobResult]:
        """Load a job result by ID"""
        job_dir = self.jobs_dir / job_id
        json_file = job_dir / "result.json"
        
        if not json_file.exists():
            return None
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return JobResult(**data)
        except Exception as e:
            self._log(f"Failed to load job {job_id}: {str(e)}", "ERROR")
            return None
    
    def list_jobs(self, status: Optional[JobStatus] = None, limit: int = 50) -> List[JobMetadata]:
        """List all jobs with optional status filter"""
        jobs = []
        
        for job_dir in self.jobs_dir.iterdir():
            if not job_dir.is_dir():
                continue
            
            metadata_file = job_dir / "metadata.json"
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata_data = json.load(f)
                    metadata = JobMetadata(**metadata_data)
                    
                    if status is None or metadata.status == status:
                        jobs.append(metadata)
                        
                except Exception as e:
                    self._log(f"Failed to load metadata for {job_dir.name}: {str(e)}", "ERROR")
        
        # Sort by creation time (newest first)
        jobs.sort(key=lambda x: x.created_at, reverse=True)
        return jobs[:limit]
    
    def export_jobs_to_excel(self, job_ids: List[str], output_file: Optional[str] = None) -> str:
        """Export multiple jobs to a single Excel file"""
        try:
            import pandas as pd
        except ImportError:
            raise ImportError("pandas is required for Excel export. Install with: pip install pandas openpyxl")
        
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = str(self.exports_dir / f"linkedin_agent_export_{timestamp}.xlsx")
        
        all_contacts = []
        job_summaries = []
        
        for job_id in job_ids:
            job_result = self.load_job_result(job_id)
            if job_result:
                # Add contacts with job reference
                for contact in job_result.contacts:
                    contact_dict = contact.dict()
                    contact_dict['job_id'] = job_id
                    contact_dict['source_url'] = job_result.metadata.input_url
                    all_contacts.append(contact_dict)
                
                # Add job summary
                job_summaries.append({
                    'job_id': job_id,
                    'status': job_result.metadata.status.value,
                    'input_url': job_result.metadata.input_url,
                    'contacts_found': len(job_result.contacts),
                    'processing_time': job_result.metadata.processing_time_seconds,
                    'created_at': job_result.metadata.created_at,
                    'completed_at': job_result.metadata.completed_at
                })
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            if all_contacts:
                df_contacts = pd.DataFrame(all_contacts)
                df_contacts.to_excel(writer, sheet_name='Contacts', index=False)
            
            if job_summaries:
                df_summaries = pd.DataFrame(job_summaries)
                df_summaries.to_excel(writer, sheet_name='Job_Summary', index=False)
        
        self._log(f"Exported {len(job_ids)} jobs to {output_file}")
        return output_file
    
    def cleanup_old_jobs(self, days_old: int = 30) -> int:
        """Clean up jobs older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        cleaned_count = 0
        
        for job_dir in self.jobs_dir.iterdir():
            if not job_dir.is_dir():
                continue
            
            metadata_file = job_dir / "metadata.json"
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata_data = json.load(f)
                    
                    created_at = datetime.fromisoformat(metadata_data['created_at'].replace('Z', '+00:00'))
                    if created_at < cutoff_date:
                        import shutil
                        shutil.rmtree(job_dir)
                        cleaned_count += 1
                        
                except Exception as e:
                    self._log(f"Failed to check job {job_dir.name} for cleanup: {str(e)}", "ERROR")
        
        self._log(f"Cleaned up {cleaned_count} old jobs")
        return cleaned_count
