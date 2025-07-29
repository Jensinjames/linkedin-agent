"""
Simplified main entry point that works without external dependencies.
This version uses local adapters and simple web scraping instead of Apify/Supabase.
"""

import asyncio
import json

# Use simple local adapter instead of Apify
from src.adapters.simple_local_adapter import SimpleLocalAdapter

async def simple_main():
    """
    Simple main function that works without external dependencies.
    
    Usage:
        python simple_main.py input.json
        echo '{"query": "https://example.com"}' | python simple_main.py
    """
    try:
        # Initialize simple local adapter
        adapter = SimpleLocalAdapter(data_dir='../storage/data')
        
        # Get input
        adapter.log_info("Starting Simple LinkedIn Agent")
        input_data = await adapter.get_input()
        
        adapter.log_info(f"Processing query: {input_data.get('query', 'No query provided')}")
        
        # Simple processing without LLM (for now)
        if 'query' in input_data:
            url = input_data['query']
            
            # Use simple web scraping instead of Apify
            from src.tools_simple import SimpleWebScraper
            scraper = SimpleWebScraper()
            
            adapter.log_info(f"Scraping contact details from: {url}")
            result = scraper.scrape_contact_details(url)
            
            # Push results
            job_id = await adapter.push_data(result)
            adapter.log_info(f"Job completed successfully. ID: {job_id}")
            
            # Print results to console for immediate feedback
            print("\n=== RESULTS ===")
            print(json.dumps(result, indent=2))
            
        else:
            adapter.log_info("No query provided in input")
            
    except Exception as e:
        adapter.log_info(f"Error occurred: {e}")
        await adapter.fail(f"Processing failed: {e}", exception=e)

if __name__ == "__main__":
    asyncio.run(simple_main())
