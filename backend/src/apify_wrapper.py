# See prior message for full code (CLI/REST wrapper for single jobs)
# Place in src/apify_wrapper.py
import sys
import json
import subprocess
import requests
from urllib.parse import urlparse
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
            if not input_path.is_relative_to(safe_root):
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
        def is_valid_webhook(url):
            # Example whitelist of allowed domains
            allowed_domains = ["example.com", "webhook.site"]
            try:
                from urllib.parse import urlparse
                import socket

                parsed_url = urlparse(url)
                domain = parsed_url.netloc

                # Check if domain is in the whitelist
                if domain not in allowed_domains:
                    return False

                # Resolve domain to IP and check if it's public
                ip = socket.gethostbyname(domain)
                private_ip_ranges = [
                    ("10.0.0.0", "10.255.255.255"),
                    ("172.16.0.0", "172.31.255.255"),
                    ("192.168.0.0", "192.168.255.255"),
                    ("127.0.0.0", "127.255.255.255"),
                    ("::1", "::1"),  # IPv6 localhost
                ]

                def is_private(ip):
                    for start, end in private_ip_ranges:
                        if start <= ip <= end:
                            return True
                    return False

                if is_private(ip):
                    return False

                return ip
            except Exception:
                return False

        if not is_valid_webhook(args.webhook):
            print(f"Error: Invalid webhook URL {args.webhook}.", file=sys.stderr)
            sys.exit(1)

        try:
            class IPEnforcingAdapter(requests.adapters.HTTPAdapter):
                def __init__(self, resolved_ip, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    self.resolved_ip = resolved_ip

                def send(self, request, *args, **kwargs):
                    request.url = request.url.replace(request.url.split('/')[2], self.resolved_ip)
                    return super().send(request, *args, **kwargs)

            resolved_ip = is_valid_webhook(args.webhook)
            if not resolved_ip:
                print(f"Error: Invalid webhook URL {args.webhook}.", file=sys.stderr)
                sys.exit(1)

            session = requests.Session()
            session.mount("http://", IPEnforcingAdapter(resolved_ip))
            session.mount("https://", IPEnforcingAdapter(resolved_ip))

            resp = session.post(args.webhook, json=result)
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