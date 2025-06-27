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
        return {"error": f"Failed to parse agent output: {e}", "raw": proc.stdout}
    return result

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)