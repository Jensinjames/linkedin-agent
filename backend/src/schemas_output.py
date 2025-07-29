"""
Enhanced output schema for LinkedIn Agent job results.
Provides structured, readable output with proper data validation.
"""
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ContactInfo(BaseModel):
    """Structured contact information schema"""
    name: Optional[str] = None
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    emails: List[str] = Field(default_factory=list)
    phones: List[str] = Field(default_factory=list)
    social_links: Dict[str, str] = Field(default_factory=dict)
    linkedin_url: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    
    @validator('emails')
    def validate_emails(cls, v):
        """Ensure emails are properly formatted"""
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return [email for email in v if re.match(email_pattern, email)]

class JobMetadata(BaseModel):
    """Job execution metadata"""
    job_id: str
    status: JobStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    processing_time_seconds: Optional[float] = None
    input_url: str
    total_contacts: int = 0
    errors_count: int = 0

class ErrorInfo(BaseModel):
    """Error information structure"""
    error_type: str
    error_message: str
    url: Optional[str] = None
    timestamp: datetime

class JobResult(BaseModel):
    """Complete job result structure"""
    metadata: JobMetadata
    contacts: List[ContactInfo] = Field(default_factory=list)
    errors: List[ErrorInfo] = Field(default_factory=list)
    summary: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def to_formatted_dict(self) -> Dict[str, Any]:
        """Return a formatted dictionary for display"""
        return {
            "job_summary": {
                "job_id": self.metadata.job_id,
                "status": self.metadata.status.value,
                "input_url": self.metadata.input_url,
                "total_contacts_found": self.metadata.total_contacts,
                "processing_time": f"{self.metadata.processing_time_seconds:.2f}s" if self.metadata.processing_time_seconds else "N/A",
                "created_at": self.metadata.created_at.isoformat(),
                "completed_at": self.metadata.completed_at.isoformat() if self.metadata.completed_at else None
            },
            "contacts": [contact.dict() for contact in self.contacts],
            "errors": [error.dict() for error in self.errors] if self.errors else [],
            "summary": self.summary,
            "statistics": {
                "total_contacts": len(self.contacts),
                "contacts_with_emails": len([c for c in self.contacts if c.emails]),
                "contacts_with_phones": len([c for c in self.contacts if c.phones]),
                "social_links_found": sum(len(c.social_links) for c in self.contacts),
                "errors_encountered": len(self.errors)
            }
        }
    
    def to_csv_data(self) -> List[Dict[str, str]]:
        """Convert to CSV-friendly format"""
        csv_data = []
        for contact in self.contacts:
            csv_data.append({
                "job_id": self.metadata.job_id,
                "name": contact.name or "",
                "title": contact.title or "",
                "company": contact.company or "",
                "location": contact.location or "",
                "emails": "; ".join(contact.emails),
                "phones": "; ".join(contact.phones),
                "linkedin_url": contact.linkedin_url or "",
                "website": contact.website or "",
                "description": contact.description or "",
                "social_links": "; ".join([f"{k}: {v}" for k, v in contact.social_links.items()])
            })
        return csv_data

class BatchJobResult(BaseModel):
    """Result for batch processing multiple URLs"""
    batch_id: str
    total_jobs: int
    completed_jobs: int
    failed_jobs: int
    processing_time_seconds: float
    created_at: datetime
    completed_at: Optional[datetime] = None
    individual_results: List[JobResult] = Field(default_factory=list)
    
    def get_all_contacts(self) -> List[ContactInfo]:
        """Get all contacts from all jobs in the batch"""
        all_contacts = []
        for result in self.individual_results:
            all_contacts.extend(result.contacts)
        return all_contacts
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get batch summary statistics"""
        all_contacts = self.get_all_contacts()
        all_errors = []
        for result in self.individual_results:
            all_errors.extend(result.errors)
        
        return {
            "batch_id": self.batch_id,
            "total_jobs": self.total_jobs,
            "completed_jobs": self.completed_jobs,
            "failed_jobs": self.failed_jobs,
            "success_rate": f"{(self.completed_jobs / self.total_jobs * 100):.1f}%" if self.total_jobs > 0 else "0%",
            "total_contacts_found": len(all_contacts),
            "total_emails_found": sum(len(c.emails) for c in all_contacts),
            "total_phones_found": sum(len(c.phones) for c in all_contacts),
            "total_errors": len(all_errors),
            "processing_time": f"{self.processing_time_seconds:.2f}s",
            "avg_time_per_job": f"{(self.processing_time_seconds / self.total_jobs):.2f}s" if self.total_jobs > 0 else "N/A"
        }
