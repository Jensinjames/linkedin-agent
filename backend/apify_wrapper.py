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
        import os
        # Define a safe root directory
        safe_root = Path("/safe/root/directory").resolve()
        # Normalize and validate the input path
        input_path = Path(args.input).resolve()
        if not str(input_path).startswith(str(safe_root)):
            print(f"Invalid input file path: {args.input}", file=sys.stderr)
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
        from urllib.parse import urlparse
        import socket
        from requests.adapters import HTTPAdapter
        from requests.sessions import Session

        # Define a whitelist of allowed domains
        # Define a whitelist of allowed webhook URLs
        allowed_domains = {"example.com", "webhook.site"}

        # Validate the webhook URL
        try:
            parsed_url = urlparse(args.webhook)
            if parsed_url.scheme not in {"http", "https"} or parsed_url.hostname not in allowed_domains:
                raise ValueError("Invalid webhook URL")
        except Exception as e:
            print(f"Invalid webhook URL: {args.webhook} ({e})", file=sys.stderr)
            sys.exit(1)

        # Resolve the IP address of the hostname
        try:
            resolved_ip = socket.gethostbyname(parsed_url.hostname)
            private_ip_ranges = [
                ("127.0.0.0", "127.255.255.255"),  # Loopback
                ("10.0.0.0", "10.255.255.255"),    # Private network
                ("192.168.0.0", "192.168.255.255") # Private network
            ]
            for start, end in private_ip_ranges:
                if socket.inet_aton(start) <= socket.inet_aton(resolved_ip) <= socket.inet_aton(end):
                    print(f"Webhook URL resolves to a private IP: {resolved_ip}", file=sys.stderr)
                    sys.exit(1)
        except Exception as e:
            print(f"Failed to resolve webhook hostname: {e}", file=sys.stderr)
            sys.exit(1)

        # Use a custom HTTP adapter to enforce the resolved IP
        class FixedIPAdapter(HTTPAdapter):
            def __init__(self, ip, *args, **kwargs):
                self.ip = ip
                super().__init__(*args, **kwargs)

            def get_connection(self, url, proxies=None):
                parsed = urlparse(url)
                fixed_url = f"{parsed.scheme}://{self.ip}{parsed.path}"
                return super().get_connection(fixed_url, proxies)

        session = Session()
        session.mount(f"https://{parsed_url.hostname}", FixedIPAdapter(resolved_ip))

        try:
            resp = session.post(parsed_url.geturl(), json=result)
            print(f"Webhook POSTed, status: {resp.status_code}")
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