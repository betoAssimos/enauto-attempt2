import os
import requests
import urllib3
import json
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = os.environ["CATC_BASE_URL"]
USERNAME = os.environ["CATC_USERNAME"]
PASSWORD = os.environ["CATC_PASSWORD"]
AUTH_PATH = "/dna/system/api/v1/auth/token"

url = f"{BASE_URL}{AUTH_PATH}"
resp = requests.post(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), verify=False)
token = resp.json()["Token"]
headers = {"X-Auth-Token": token}

device_url = f"{BASE_URL}/dna/intent/api/v1/network-device"
def fetch(offset, limit):
    r = requests.get(
        device_url,
        headers=headers,
        params={"offset": offset, "limit": limit},
        verify=False,
    )
    return r.json()["response"]
LIMIT = 2
offset = 1
all_devices = []

while True:
    page = fetch(offset, LIMIT)
    if not page:
        break
    print(f"offset: {offset}, page size: {len(page)}, total so far: {len(all_devices)}")
    all_devices += page
    offset += LIMIT
