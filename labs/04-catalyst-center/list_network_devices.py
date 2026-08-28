import os
import requests
import urllib3
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = os.environ["CATC_BASE_URL"]
USERNAME = os.environ["CATC_USERNAME"]
PASSWORD = os.environ["CATC_PASSWORD"]

def get_token():
    """Get a token from the Catalyst Center API."""
    url = f"{BASE_URL}/dna/system/api/v1/auth/token"
    resp = requests.post(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), verify=False)
    resp.raise_for_status()
    return resp.json()["Token"]

def get_device_list(token):
    """Get a list of network devices from the Catalyst Center API."""
    url = f"{BASE_URL}/dna/intent/api/v1/network-device"
    headers = {"X-Auth-Token": token}
    resp = requests.get(url, headers=headers, verify=False)
    resp.raise_for_status()
    data = resp.json()
    print("top-level keys:", list(data.keys()))
    print("count:", len(data["response"]))
    return resp.json()["response"]

if __name__ == "__main__":
    token = get_token()
    devices = get_device_list(token)

    for device in devices:
        print(f"Device Name: {device['hostname']}, IP Address: {device['managementIpAddress']}, Type: {device['type']}")