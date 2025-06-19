import asyncio
from adapters.local_adapter import LocalAdapter
from main import main

if __name__ == "__main__":
    asyncio.run(main(LocalAdapter()))