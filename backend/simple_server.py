"""
Simple FastAPI server for the simplified LinkedIn agent.
This version doesn't require Redis, Supabase, or Apify - just local processing.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from src.adapters.simple_local_adapter import SimpleLocalAdapter
from src.tools_simple import SimpleWebScraper

app = FastAPI(
    title="Simple LinkedIn Agent API",
    description="Simplified LinkedIn Agent without external dependencies",
    version="1.0.0"
)

# Enable CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str
    max_depth: Optional[int] = 2
    include_summary: Optional[bool] = False
    
class ContactResponse(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    emails: list[str] = []
    phones: list[str] = []
    social_links: dict[str, str] = {}
    linkedin_url: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None

class JobSummaryResponse(BaseModel):
    job_id: str
    status: str
    input_url: str
    total_contacts_found: int
    processing_time: str
    created_at: str
    completed_at: Optional[str] = None

class QueryResponse(BaseModel):
    job_summary: JobSummaryResponse
    contacts: list[ContactResponse]
    errors: list[dict] = []
    summary: Optional[str] = None
    statistics: dict

@app.get("/")
async def root():
    return {
        "message": "Simple LinkedIn Agent API",
        "status": "running",
        "version": "1.0.0",
        "description": "Simplified version without external dependencies"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "simple-linkedin-agent"}

@app.post("/scrape", response_model=QueryResponse)
async def scrape_contact_details(request: QueryRequest):
    """
    Scrape contact details from a URL without external dependencies.
    """
    try:
        # Initialize adapter with relative path
        adapter = SimpleLocalAdapter(data_dir='../storage/data')
        
        # Log the request
        adapter.log_info(f"Processing scrape request for: {request.query}")
        
        # Use simple web scraper
        scraper = SimpleWebScraper()
        result = scraper.scrape_contact_details(request.query)
        
        # Save results with input URL
        job_id = await adapter.push_data(result, input_url=request.query)
        
        # Get the saved job result for proper formatting
        job_result = adapter.storage_manager.load_job_result(job_id)
        
        if job_result:
            # Return structured response
            return QueryResponse(**job_result.to_formatted_dict())
        else:
            # Fallback response if job result not found
            contacts = []
            if result.get('contacts'):
                for contact_data in result['contacts']:
                    contacts.append(ContactResponse(**contact_data))
            
            job_summary = JobSummaryResponse(
                job_id=job_id,
                status="completed",
                input_url=request.query,
                total_contacts_found=len(contacts),
                processing_time="N/A",
                created_at="unknown"
            )
            
            return QueryResponse(
                job_summary=job_summary,
                contacts=contacts,
                statistics={
                    "total_contacts": len(contacts),
                    "contacts_with_emails": len([c for c in contacts if c.emails]),
                    "contacts_with_phones": len([c for c in contacts if c.phones])
                }
            )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

@app.post("/process")
async def process_query(request: QueryRequest):
    """
    Process a query using the simplified main function.
    """
    try:
        # Initialize adapter
        adapter = SimpleLocalAdapter(data_dir='../storage/data')
        
        adapter.log_info(f"Processing query: {request.query}")
        
        # Use simple web scraping
        from src.tools_simple import SimpleWebScraper
        scraper = SimpleWebScraper()
        
        adapter.log_info(f"Scraping contact details from: {request.query}")
        result = scraper.scrape_contact_details(request.query)
        
        # Push results with input URL
        job_id = await adapter.push_data(result, input_url=request.query)
        adapter.log_info(f"Job completed successfully. ID: {job_id}")
        
        # Get the saved job result for proper formatting
        job_result = adapter.storage_manager.load_job_result(job_id)
        
        if job_result:
            # Return structured response
            return QueryResponse(**job_result.to_formatted_dict())
        else:
            # Fallback response
            contacts = []
            if result.get('contacts'):
                for contact_data in result['contacts']:
                    contacts.append(ContactResponse(**contact_data))
            
            job_summary = JobSummaryResponse(
                job_id=job_id,
                status="completed", 
                input_url=request.query,
                total_contacts_found=len(contacts),
                processing_time="N/A",
                created_at="unknown"
            )
            
            return QueryResponse(
                job_summary=job_summary,
                contacts=contacts,
                statistics={
                    "total_contacts": len(contacts),
                    "contacts_with_emails": len([c for c in contacts if c.emails]),
                    "contacts_with_phones": len([c for c in contacts if c.phones])
                }
            )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.get("/jobs")
async def list_jobs():
    """List all jobs with their status"""
    try:
        adapter = SimpleLocalAdapter(data_dir='../storage/data')
        jobs = adapter.storage_manager.list_jobs(limit=50)
        
        return {
            "jobs": [job.dict() for job in jobs],
            "total": len(jobs)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list jobs: {str(e)}")

@app.get("/jobs/{job_id}")
async def get_job_result(job_id: str):
    """Get detailed job result by ID"""
    try:
        adapter = SimpleLocalAdapter(data_dir='../storage/data')
        job_result = adapter.storage_manager.load_job_result(job_id)
        
        if not job_result:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return job_result.to_formatted_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job: {str(e)}")

@app.get("/jobs/{job_id}/summary")
async def get_job_summary(job_id: str):
    """Get text summary of job result"""
    try:
        adapter = SimpleLocalAdapter(data_dir='../storage/data')
        job_result = adapter.storage_manager.load_job_result(job_id)
        
        if not job_result:
            raise HTTPException(status_code=404, detail="Job not found")
        
        summary = adapter.storage_manager._generate_text_summary(job_result)
        return {"job_id": job_id, "summary": summary}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get summary: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
