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
#AUTH_HEADER = {"X-Auth-Token": TOKEN_KEY, "Content-Type": "application/json" } 
#TOKEN_KEY = "Token"   
VERIFY = False
# for lab, verify false so you dont use certificate. In production this should always be true.
   

def get_token():
    """Get a token from the Catalyst Center API."""
    url = f"{BASE_URL}{AUTH_PATH}"
    resp = requests.post(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), verify=VERIFY)
    resp.raise_for_status()
    print("status:", resp.status_code)
    print("headers:", dict(resp.headers))
    print("body:", resp.text[:100])
    return resp.json()["Token"]

def authenticated_get(token, path):
    """Make an authenticated GET request to the Catalyst Center API."""
    url = f"{BASE_URL}{path}"
    AUTH_HEADER = { "X-Auth-Token": token }
    resp = requests.get(url, headers=AUTH_HEADER, verify=VERIFY)
    print("status:", resp.status_code)
    print(resp.text.encode('utf8'))
    resp.raise_for_status()
    return resp.json()

if __name__ == "__main__":
    token = get_token()
    print("token length:", len(token))

    resp = authenticated_get(token, "/dna/intent/api/v1/dnac-packages")