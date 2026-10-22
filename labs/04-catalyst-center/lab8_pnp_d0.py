import os
import requests
import urllib3
import json
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import time

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = os.environ["CATC_BASE_URL"]
USERNAME = os.environ["CATC_USERNAME"]
PASSWORD = os.environ["CATC_PASSWORD"]

def get_token():
    """Get an authenticatioon token fromo Catalyst Center API"""
    AUTH_PATH = "/dna/system/api/v1/auth/token"
    url=f"{BASE_URL}{AUTH_PATH}"
    resp = requests.post(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), verify=False)
    resp.raise_for_status()
    return resp.json()["Token"]

def get_device_list( headers):
    """Get a list of network devices from DNAC"""
    device_url = "/dna/intent/api/v1/onboarding/pnp-device"
    url = f"{BASE_URL}{device_url}"
    resp = requests.get(url, headers=headers, verify=False)
    resp.raise_for_status()
    data = resp.json()
    return data

def get_sites(headers):
    """Get a list of sites from DNAC"""
    site_url = "/dna/intent/api/v1/site"
    url = f"{BASE_URL}{site_url}"
    resp = requests.get(url, headers=headers, verify=False)
    resp.raise_for_status()
    data = resp.json()
    return data

def post_claim(claim, headers):
    url = f"{BASE_URL}/dna/intent/api/v1/onboarding/pnp-device/site-claim"
    r = requests.post(url, json=claim, headers=headers, verify=False)

    print("HTTP Status:", r.status_code)
    print("Response:", json.dumps(r.json(), indent=2))

    r.raise_for_status()
    return r.json()

def get_task(task_id, headers):
    url = f"{BASE_URL}/dna/intent/api/v1/task/{task_id}"
    r = requests.get(url, headers=headers, verify=False)
    r.raise_for_status()

    task = r.json()["response"]
    print("End time:", task.get("endTime"))
    print("Is error:", task.get("isError"))
    print("Failure reason:", task.get("failureReason"))
    return task

def wait_for_task(task_id, headers, timeout=30):
    for _ in range(timeout):
        t = get_task(task_id, headers)
        if t.get("endTime"):
            if t.get("isError"):
                raise RuntimeError(t.get("failureReason", "task failed"))
            return t
        time.sleep(2)
    raise TimeoutError("task did not complete in time")


TOKEN = get_token()
new_headers = {"X-Auth-Token": TOKEN, "Content-Type": "application/json"}
print("Authenticated; token lenght:", len(TOKEN))
devices = get_device_list(new_headers)
print(f"Devices: {devices}")
sites = get_sites(new_headers)
print(f"Sites: {sites}")
claim = {
    "deviceId": "a1b2c3d4-0000-1111-2222-333344445555",
    "siteId": "a1b2c3d4-0000-1111-2222-333344446666",
    "type": "Default",
    "imageInfo": {
        "imageId": "ios-xe-17.12.img.uuid", "skip": False
    },
    "configInfo": {
        "configId": "day0-branch-template-uuid",
        "configParameters": [
            {"key": "HOSTNAME", "value": "BRANCH07-SW01"},
            {"key": "MGMT_IP", "value": "10.7.0.2"}
        ]
    },
}
# r = post_claim(claim, new_headers)
# print(r)
# task = r["response"]["taskId"]
# result = wait_for_task(task, new_headers)
# print("Task complete:", result["progress"])