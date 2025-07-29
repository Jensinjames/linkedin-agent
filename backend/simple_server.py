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
    
class QueryResponse(BaseModel):
    job_id: str
    results: dict
    status: str

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
        
        # Save results
        job_id = await adapter.push_data(result)
        
        return QueryResponse(
            job_id=job_id,
            results=result,
            status="completed"
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
        
        # Push results
        job_id = await adapter.push_data(result)
        adapter.log_info(f"Job completed successfully. ID: {job_id}")
        
        return QueryResponse(
            job_id=job_id,
            results=result,
            status="completed"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
