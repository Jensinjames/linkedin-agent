"""LinkedIn crawler module."""

from typing import Any, Dict

from ..tools import call_contact_details_scraper


async def run_linkedin_crawler(
    query: str,
    max_depth: int = 2,
    include_socials: bool = True,
) -> Dict[str, Any]:
    """
    Execute a LinkedIn contact details crawler for the given query string of LinkedIn URLs.
    
    Parameters:
        query (str): Whitespace-separated LinkedIn URLs to crawl.
        max_depth (int, optional): Maximum depth for crawling connections. Defaults to 2.
        include_socials (bool, optional): Whether to include social media fields in the results. Defaults to True.
    
    Returns:
        Dict[str, Any]: A dictionary containing the original query and the list of extracted contact details.
    
    Raises:
        ValueError: If no valid LinkedIn URLs are provided in the query.
    """

    urls = [part.strip() for part in query.split() if part.strip()]
    start_urls = [{"url": url} for url in urls if url.startswith("http")]
    if not start_urls:
        raise ValueError("No LinkedIn URLs provided")

    data = await call_contact_details_scraper(start_urls, max_depth=max_depth)

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

