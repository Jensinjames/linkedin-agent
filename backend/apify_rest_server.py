import os
import json
import logging
from typing import Any, Dict

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Apify REST Server",
    description="API for running LinkedIn Agent tasks asynchronously.",
    version="1.1.0"
)

def validate_input(data: Any) -> None:
    # Example validation: data should be a dict and contain required keys
    if not isinstance(data, dict):
        raise ValueError("Input data must be a JSON object.")
    def validate_input(data: dict) -> None:
    # Validate that data is a dict
    if not isinstance(data, dict):
        raise ValueError("Input data must be a JSON object.")

    # Check required 'query' field
    if "query" not in data:
        raise ValueError("Missing 'query' field in input.")
    if not isinstance(data["query"], str):
        raise ValueError("'query' field must be a string.")

    # Optional: Validate modelName if present
    valid_models = ["gpt-4o-mini", "gpt-4o"]
    if "modelName" in data:
        if data["modelName"] not in valid_models:
            raise ValueError(f"'modelName' must be one of: {valid_models}")

    # Optional: Validate summarizeResults if present
    if "summarizeResults" in data:
        if not isinstance(data["summarizeResults"], bool):
            raise ValueError("'summarizeResults' must be a boolean.")
@app.post(
    "/run",
    summary="Run the agent",
    description="Runs the agent with the provided input data and returns the result."
)
async def run_agent(request: Request) -> JSONResponse:
    try:
        input_data = await request.json()
        validate_input(input_data)
    except Exception as e:
        logger.error(f"Invalid input: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid input: {e}")

    try:
        proc = await asyncio.create_subprocess_exec(
            "python", "-m", "src.cli",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate(input=json.dumps(input_data).encode())

        if proc.returncode != 0:
            logger.error(f"Subprocess failed: {stderr.decode()}")
            return JSONResponse(status_code=500, content={"error": stderr.decode()})

        try:
            result = json.loads(stdout.decode())
            return JSONResponse(content=result)
        except Exception as e:
            logger.error(f"Error parsing agent output: {e}")
            logger.error(f"Raw output: {stdout.decode()}")
            return JSONResponse(
                status_code=500,
                content={"error": "Failed to process the agent output. Please contact support."},
            )

    except Exception as e:
        logger.exception(f"Unexpected server error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    uvicorn.run(app, host=host, port=port)
