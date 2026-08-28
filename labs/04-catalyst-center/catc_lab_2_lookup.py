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
def fetch(params=None):
    r = requests.get(device_url, headers=headers, params=params, verify=False)
    return r.json()["response"]
# baseline — no parameters, this is your Step 2 result
baseline1 = fetch()
print("baseline1:", [d["hostname"] for d in baseline1])
print("-------------------------------------------------------")

# TODO 1 — same call, both parameters, page size 2, offset value A
baseline2 = fetch(params={"offset": 5, "limit": 2})
print("baseline2:", [d["hostname"] for d in baseline2])
print("-------------------------------------------------------")
# TODO 2 — same call, both parameters, page size 2, offset value B
#baseline3 = fetch(params={"offset": 0, "limit": 2})
#print("baseline3:", [d["hostname"] for d in baseline3])
#print("-------------------------------------------------------")
#          A and B differ by one. Pick the two candidates.

def fetch_raw(params=None):
    r = requests.get(device_url, headers=headers, params=params, verify=False)
    print(json.dumps(r.json(), indent=2))
    return r.status_code, r.json()

print(fetch_raw({"startIndex": 3, "limit": 2}))

# print each result the same way as baseline and compare by eye

r = requests.get(f"{device_url}/count", headers=headers, verify=False)
print(r.status_code, r.json())
print(json.dumps(r.json(), indent=2))