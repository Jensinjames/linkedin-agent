import sys
import json
import csv
from .base import PlatformAdapter

class LocalAdapter(PlatformAdapter):
    async def get_input(self):
        # Accept input from a file or stdin
        if len(sys.argv) > 1:
            with open(sys.argv[1]) as f:
                data = json.load(f)
        else:
            data = json.load(sys.stdin)

        if data.get("inputType") == "csv" and data.get("inputPath"):
            with open(data["inputPath"], newline="") as csvfile:
                reader = csv.reader(csvfile)
                csv_urls = [row[0] for row in reader if row]
            data["csv_urls"] = csv_urls

        return data

    async def push_data(self, data):
        print(json.dumps(data, indent=2))

    def log_info(self, msg):
        print(f"[INFO] {msg}")

    async def fail(self, status_message, exception=None):
        """
        Print an error message and terminate the program with exit code 1.
        
        If an exception is provided, its string representation is also printed.
        """
        print(f"[ERROR] {status_message}")
        if exception:
            print(str(exception))
        sys.exit(1)
