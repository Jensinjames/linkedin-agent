import asyncio
from src.adapters.apify_adapter import ApifyAdapter
from src.main import main

if __name__ == "__main__":
    asyncio.run(main(ApifyAdapter()))