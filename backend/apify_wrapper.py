import sys
import json
import subprocess
import requests
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="CLI wrapper for LinkedIn Agent with optional webhook callback")
    parser.add_argument("--input", "-i", type=str, help="Input JSON file (or pass via stdin)")
    parser.add_argument("--webhook", "-w", type=str, help="Webhook URL to POST results to (n8n/Zapier compatible)")
    args = parser.parse_args()

    # Read input
    if args.input:
        with open(args.input) as f:
            input_data = json.load(f)
    else:
        input_data = json.load(sys.stdin)

    # Write input to a temporary file for the CLI
    temp_input = Path("input_webhook_tmp.json")
    with temp_input.open("w") as f:
        json.dump(input_data, f)

    # Run the agent via the CLI (reuse your python -m src.cli ...)
    proc = subprocess.run(
        [sys.executable, "-m", "src.cli", str(temp_input)],
        capture_output=True,
        text=True
    )

    # Get the result
    if proc.returncode != 0:
        print(f"Agent failed: {proc.stderr}", file=sys.stderr)
        sys.exit(proc.returncode)

    try:
        result = json.loads(proc.stdout)
    except Exception as e:
        print(f"Failed to parse agent output: {e}\n{proc.stdout}", file=sys.stderr)
        sys.exit(1)

    # POST to webhook if provided
    if args.webhook:
        from urllib.parse import urlparse

        # Define a whitelist of allowed domains
        allowed_domains = {"example.com", "webhook.site"}

        # Parse the webhook URL
        parsed_url = urlparse(args.webhook)
        if parsed_url.hostname not in allowed_domains:
            print(f"Invalid webhook URL: {args.webhook}", file=sys.stderr)
            sys.exit(1)

        try:
            resp = requests.post(args.webhook, json=result)
            print(f"Webhook POSTed, status: {resp.status_code}")
        except Exception as e:
            print(f"Failed to POST to webhook: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Print result to stdout (for synchronous n8n/zapier call)
        print(json.dumps(result, indent=2))

    # Clean up temp file
    temp_input.unlink()

if __name__ == "__main__":
    main()