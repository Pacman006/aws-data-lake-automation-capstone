#!/usr/bin/env python3
"""Check that the read API rejects anonymous calls and accepts a valid JWT."""
import argparse
import json
import os
import urllib.error
import urllib.request


def request(url, token=None):
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            return res.status, json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return exc.code, {"message": exc.read().decode("utf-8")[:250]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-url", required=True)
    parser.add_argument("--device", default="vehicle-001")
    args = parser.parse_args()
    url = args.api_url.rstrip("/") + "/devices/" + args.device + "/latest"
    anonymous_status, _ = request(url)
    print("Unauthenticated GET:", anonymous_status, "(expect 401)")
    if anonymous_status != 401:
        print("WARNING: API may not be protected as expected")
        return 1
    token = os.getenv("DATA_LAKE_ACCESS_TOKEN")
    if not token:
        print("Set DATA_LAKE_ACCESS_TOKEN to check authorized access. No token is logged.")
        return 0
    status, payload = request(url, token)
    print("Authenticated GET:", status, payload)
    return 0 if status == 200 else 1


if __name__ == "__main__":
    raise SystemExit(main())
