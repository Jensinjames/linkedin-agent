# See prior message for full code (CLI/REST wrapper for single jobs)
# Place in src/apify_wrapper.py
import sys
import os
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
        safe_root = Path("/safe/input/directory").resolve()
        input_path = Path(args.input).resolve()
        try:
            # Normalize and ensure input_path is strictly within safe_root
            if os.path.commonpath([safe_root, input_path]) != str(safe_root):
                raise ValueError
        except ValueError:
            print(f"Error: Input file path {args.input} is not allowed.", file=sys.stderr)
            sys.exit(1)
        with input_path.open() as f:
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
        import ipaddress
        from urllib.parse import urlparse
        import socket

        def is_valid_webhook(url):
            try:
                parsed = urlparse(url)
                if parsed.scheme != "https":
                    return False
                host = parsed.hostname
                if not host:
                    return False
                # Resolve all A/AAAA records
                for family in (socket.AF_INET, socket.AF_INET6):
                    try:
                        infos = socket.getaddrinfo(host, None, family)
                    except socket.gaierror:
                        continue
                    for info in infos:
                        ip = info[4][0]
                        ip_obj = ipaddress.ip_address(ip)
                        if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_reserved or ip_obj.is_link_local or ip_obj.is_multicast:
                            return False
                return True
            except Exception:
                return False

        if not is_valid_webhook(args.webhook):
            print(f"Error: Invalid webhook URL {args.webhook}.", file=sys.stderr)
            sys.exit(1)

        try:
            resp = requests.post(args.webhook, json=result, timeout=10)
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