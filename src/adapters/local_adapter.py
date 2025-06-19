import sys
import json
from .base import PlatformAdapter

class LocalAdapter(PlatformAdapter):
    async def get_input(self):
        # Accept input from a file or stdin
        if len(sys.argv) > 1:
            with open(sys.argv[1]) as f:
                return json.load(f)
        else:
            return json.load(sys.stdin)

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
