"""LinkedIn crawler module."""

from typing import Any, Dict

from ..tools import call_contact_details_scraper


async def run_linkedin_crawler(
    query: str,
    max_depth: int = 2,
    include_socials: bool = True,
) -> Dict[str, Any]:
    """Run the Apify Contact Details Scraper for provided LinkedIn URLs."""

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

