"""
This demonstrates what FileResponse actually sends.
Run this to see the raw HTTP response.
"""
import requests

# Make a request to your endpoint
response = requests.get("http://localhost:8000/zonal_stats?polygon_url=...&raster_url=...")

print("=== HTTP RESPONSE HEADERS ===")
for key, value in response.headers.items():
    print(f"{key}: {value}")

print("\n=== RESPONSE BODY (first 100 bytes) ===")
print(response.content[:100])  # First 100 bytes of the file
print(f"\nTotal body size: {len(response.content)} bytes")

print("\n=== WHAT THE CLIENT RECEIVES ===")
print("1. Headers tell browser: 'This is a file download'")
print("2. Response body contains the actual file bytes")
print("3. Browser saves body to disk with the filename from header")


