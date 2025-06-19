import asyncio
from adapters.apify_adapter import ApifyAdapter
from main import main

if __name__ == "__main__":
    asyncio.run(main(ApifyAdapter()))