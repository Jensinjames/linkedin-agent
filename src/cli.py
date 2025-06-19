import asyncio
from src.adapters.local_adapter import LocalAdapter
from src.main import main

if __name__ == "__main__":
    asyncio.run(main(LocalAdapter()))
