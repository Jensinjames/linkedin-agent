from fastapi import FastAPI, Request
import uvicorn
import subprocess
import json

app = FastAPI()

@app.post("/run")
async def run_agent(request: Request):
    input_data = await request.json()

    # Write the input to a file or pass as stdin
    proc = subprocess.run(
        ["python", "-m", "src.cli"],
        input=json.dumps(input_data),
        capture_output=True,
        text=True
    )
    if proc.returncode != 0:
        return {"error": proc.stderr}
    try:
        result = json.loads(proc.stdout)
    except Exception as e:
        # Log the exception details and raw output for debugging
        print(f"Error parsing agent output: {e}")
        print(f"Raw output: {proc.stdout}")
        # Return a generic error message to the user
        return {"error": "Failed to process the agent output. Please contact support."}
    return result

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)