#!/usr/bin/env python3
"""Simple script to test Greenhouse API connection."""

import os
from base64 import b64encode

import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_KEY = os.environ.get("TAP_GREENHOUSE_CLIENT_KEY")
CLIENT_SECRET = os.environ.get("TAP_GREENHOUSE_CLIENT_SECRET")

print(f"Client Key: {CLIENT_KEY[:10]}..." if CLIENT_KEY else "Client Key: Not set")
print(f"Client Secret: {CLIENT_SECRET[:10]}..." if CLIENT_SECRET else "Client Secret: Not set")
print()

token_url = "https://auth.greenhouse.io/token"
auth_string = b64encode(f"{CLIENT_KEY}:{CLIENT_SECRET}".encode()).decode()


def try_token_request(description: str, data: dict) -> str | None:
    """Try to get an OAuth token with the given parameters."""
    print(f"\n{'=' * 60}")
    print(f"Trying: {description}")
    print(f"{'=' * 60}")
    print(f"Data: {data}")

    response = requests.post(
        token_url,
        headers={
            "Authorization": f"Basic {auth_string}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data=data,
    )

    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")

    if response.status_code == 200:
        return response.json().get("access_token")
    return None


# Try various scope formats
scope_variations = [
    ("No scope parameter", {"grant_type": "client_credentials"}),
    ("Empty scope", {"grant_type": "client_credentials", "scope": ""}),
    ("harvest:* wildcard", {"grant_type": "client_credentials", "scope": "harvest:*"}),
    ("Colon-separated format", {"grant_type": "client_credentials", "scope": "harvest:candidates:list"}),
    ("Dot-separated format", {"grant_type": "client_credentials", "scope": "candidates.read"}),
    ("Space-separated multiple", {"grant_type": "client_credentials", "scope": "harvest:candidates:list harvest:applications:list"}),
]

access_token = None
for description, data in scope_variations:
    token = try_token_request(description, data)
    if token:
        access_token = token
        print(f"\n*** SUCCESS! Got token: {token[:30]}...")
        break

# If we got a token, try to use it
if access_token:
    print(f"\n{'=' * 60}")
    print("Testing V3 API with Bearer token")
    print(f"{'=' * 60}")

    for endpoint in ["/v3/applications", "/v3/candidates", "/v3/jobs"]:
        url = f"https://harvest.greenhouse.io{endpoint}"
        response = requests.get(
            url,
            headers={"Authorization": f"Bearer {access_token}", "Accept": "application/json"},
            params={"per_page": 1},
        )
        print(f"\n{endpoint}: {response.status_code}")
        print(f"Response: {response.text[:200]}")

# Also try V1 API with different auth approaches
print(f"\n{'=' * 60}")
print("Testing V1 API with Basic Auth")
print(f"{'=' * 60}")

for name, key in [("client_key", CLIENT_KEY), ("client_secret", CLIENT_SECRET)]:
    auth = b64encode(f"{key}:".encode()).decode()
    response = requests.get(
        "https://harvest.greenhouse.io/v1/applications",
        headers={"Authorization": f"Basic {auth}", "Accept": "application/json"},
        params={"per_page": 1},
    )
    print(f"\nUsing {name}: {response.status_code}")
    print(f"Response: {response.text[:200]}")
