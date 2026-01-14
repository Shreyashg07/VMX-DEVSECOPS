import requests

def upload_report(api_url, api_key, report):
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["x-api-key"] = api_key

    url = f"{api_url}/incidents"

    r = requests.post(url, json=report, headers=headers, timeout=10)
    if r.status_code >= 300:
        raise Exception(f"Server returned {r.status_code}: {r.text}")

    print("✓ Report uploaded successfully")
