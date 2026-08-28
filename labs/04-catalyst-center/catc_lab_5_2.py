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
AUTH_PATH = "/dna/system/api/v1/auth/token"

url = f"{BASE_URL}{AUTH_PATH}"
resp = requests.post(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), verify=False)
resp.raise_for_status()
token = resp.json()["Token"]

url_2 = f"{BASE_URL}/dna/intent/api/v1/network-device"
headers = {"X-Auth-Token": token}
resp_2 = requests.get(url_2, headers=headers, verify=False)
resp_2.raise_for_status()
print("top-level keys:", list(resp_2.json().keys()))
devices_2 = resp_2.json()["response"]
print("count:", len(devices_2))
print("fields:", sorted(devices_2[0].keys()))
print(devices_2[0]["id"] == devices_2[0]["instanceUuid"])