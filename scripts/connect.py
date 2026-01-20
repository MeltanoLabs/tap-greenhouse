#!/usr/bin/env -S uv run

# ruff: noqa: T201

"""Simple script to test Greenhouse V3 API connection."""

import http
import os
import sys
from base64 import b64encode

import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.environ.get("TAP_GREENHOUSE_CLIENT_ID")
CLIENT_SECRET = os.environ.get("TAP_GREENHOUSE_CLIENT_SECRET")

print(f"Client ID: {CLIENT_ID[:10]}..." if CLIENT_ID else "Client ID: Not set")
print(f"Client Secret: {CLIENT_SECRET[:10]}..." if CLIENT_SECRET else "Client Secret: Not set")
print()

if not CLIENT_ID or not CLIENT_SECRET:
    print("ERROR: Both TAP_GREENHOUSE_CLIENT_ID and TAP_GREENHOUSE_CLIENT_SECRET must be set")
    sys.exit(1)

token_url = "https://auth.greenhouse.io/token"  # noqa: S105
auth_string = b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()

print("Requesting OAuth token...")
response = requests.post(
    token_url,
    headers={
        "Authorization": f"Basic {auth_string}",
        "Content-Type": "application/x-www-form-urlencoded",
    },
    data={"grant_type": "client_credentials"},
    timeout=10,
)

print(f"Status: {response.status_code}")

if response.status_code != http.HTTPStatus.OK:
    print(f"Error: {response.text}")
    print("\nIf you see 'Client application is not requesting any scopes', your OAuth credential")
    print("needs scopes configured in Greenhouse Dev Center → API Credential Management → Edit credential")
    sys.exit(1)

access_token = response.json().get("access_token")
print(f"Got token: {access_token[:30]}...")

# Test V3 API endpoints
print(f"\n{'=' * 60}")
print("Testing V3 API endpoints")
print(f"{'=' * 60}")

endpoints = [
    "/v3/applications",
    "/v3/candidates",
    "/v3/jobs",
    "/v3/users",
    "/v3/departments",
    "/v3/offices",
]

for endpoint in endpoints:
    url = f"https://harvest.greenhouse.io{endpoint}"
    response = requests.get(
        url,
        headers={"Authorization": f"Bearer {access_token}", "Accept": "application/json"},
        params={"per_page": 1},
        timeout=10,
    )
    status = "✓" if response.status_code == http.HTTPStatus.OK else "✗"
    print(f"{status} {endpoint}: {response.status_code}")
    if response.status_code != http.HTTPStatus.OK:
        print(f"  Error: {response.text[:100]}")
