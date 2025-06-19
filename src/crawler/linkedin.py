# __init__.py will be added to src/crawler/ directory if missing.

async def run_linkedin_crawler(query: str, max_depth: int = 2, include_socials: bool = True):
    # Implement your actual crawling logic here
    # For demonstration, return a dummy result with the new fields
    return {
        "query": query,
        "max_depth": max_depth,
        "include_socials": include_socials,
        "result": "LinkedIn data goes here"
    }