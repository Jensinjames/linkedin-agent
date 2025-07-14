"""Core crawler functionality for LinkedIn data extraction."""

from typing import Any, Dict

from ..services.apify.scraper_service import ContactDetailsScraperService
from ..exceptions import CrawlerError


class LinkedInCrawler:
    """Core crawler for LinkedIn contact details extraction."""
    
    def __init__(self, scraper_service: ContactDetailsScraperService):
        """
        Initialize the crawler with a scraper service.
        
        Args:
            scraper_service: Service for scraping contact details
        """
        self.scraper_service = scraper_service
    
    async def crawl_urls(
        self,
        query: str,
        max_depth: int = 2,
        include_socials: bool = True,
    ) -> Dict[str, Any]:
        """
        Extract contact details from LinkedIn URLs in the query.
        
        Args:
            query: Whitespace-separated LinkedIn URLs to crawl
            max_depth: Maximum depth for crawling connections
            include_socials: Whether to include social media fields
            
        Returns:
            Dictionary containing the original query and extracted contact details
            
        Raises:
            CrawlerError: If no valid URLs are provided or crawling fails
        """
        urls = [part.strip() for part in query.split() if part.strip()]
        start_urls = [{"url": url} for url in urls if url.startswith("http")]
        
        if not start_urls:
            raise CrawlerError("No valid URLs provided in query")

        try:
            data = await self.scraper_service.scrape_contact_details(
                start_urls, 
                max_depth=max_depth
            )
        except Exception as e:
            raise CrawlerError("Failed to scrape contact details", e) from e

        if not include_socials:
            for record in data:
                for field in (
                    "linkedIns",
                    "twitters", 
                    "facebooks",
                    "instagrams",
                    "youtubes",
                ):
                    record.pop(field, None)

        return {"query": query, "results": data}


# Backward compatibility function
async def run_linkedin_crawler(
    query: str,
    max_depth: int = 2,
    include_socials: bool = True,
) -> Dict[str, Any]:
    """
    Legacy function for backward compatibility.
    
    This function maintains the existing interface while using the new crawler class.
    """
    scraper_service = ContactDetailsScraperService()
    crawler = LinkedInCrawler(scraper_service)
    return await crawler.crawl_urls(query, max_depth, include_socials)
