import sys

import requests

try:
    response = requests.get("http://localhost:8001/api/v1/search/health/", timeout=5)
    response.raise_for_status()
    print(response.text)
except requests.exceptions.ConnectionError as e:
    print(f"Connection Error: {e}", file=sys.stderr)
    print("Is the Django server running on http://localhost:8001/ ?", file=sys.stderr)
    sys.exit(1)
except requests.exceptions.Timeout as e:
    print(f"Timeout Error: {e}", file=sys.stderr)
    print(
        "The request timed out. The server might be slow or unresponsive.",
        file=sys.stderr,
    )
    sys.exit(1)
except requests.exceptions.RequestException as e:
    print(f"Request Error: {e}", file=sys.stderr)
    sys.exit(1)
