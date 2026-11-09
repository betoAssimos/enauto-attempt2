import os
import requests
import urllib3
import json
import time
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

# Check environment load
# from dotenv import find_dotenv

# print("dotenv file:", find_dotenv())
# load_dotenv()
# print("MERAKI_HOST:", os.getenv("MERAKI_HOST"))

# Initialize environment and remove certificate warning
load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables
BASE_URL = os.environ["MERAKI_HOST"]
API_KEY = os.environ["MERAKI_API_KEY"]

def get_organization(session):
    url = f"{BASE_URL}/organizations"
    r = get_with_retry(session, url)
    return r

def show_org(org):
    for organization in org:
        print(organization["id"], organization["name"])

def  get_networks(session, org_id):
    url = f"{BASE_URL}/organizations/{org_id}/networks"
    r = get_with_retry(session, url)
    return r

def get_devices(session, org_id):
    url = f"{BASE_URL}/organizations/{org_id}/devices"
    params = {"perPage": 3}
    r = get_with_retry(session, url, params=params)
    return r

def get_all_devices(session, first_page):
    page = first_page
    all_devices = page.json()

    while "next" in page.links:
        next_url = page.links["next"]["url"]
        page = get_with_retry(session, next_url)
        page.raise_for_status()
        all_devices.extend(page.json())

    return all_devices

def show_unnamed_devices(devices, network_id):
    for device in devices:
        if device["networkId"] == network_id and device["name"] == "":
            print(f"{device['serial']} | {device['model']} | {device['productType']}")

def get_with_retry(session, url, params=None):
    for attempt in range(3):
        r = session.get(url, params=params)

        if r.status_code != 429:
            return r

        if attempt < 2:
            wait_seconds = int(r.headers["Retry-After"])
            time.sleep(wait_seconds)

    return r

# Start
if __name__ == "__main__":
    # 1. Authenticate
    session = requests.Session()
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    session.headers.update(headers)

    org = get_organization(session)
    print(f"Status code for get_org: {org.status_code}")
    print("*"*40)
    if org.status_code == 200:
        show_org(org.json())
        # Iterate under an organization
        for organization in org.json():
            network = get_networks(session, organization["id"])
            print(f"Status code for get network: {network.status_code}")
            print(f"{network.text}")
            devices = get_devices(session, organization["id"])
            print("*"*40)
            print(f"Status code for get device: {devices.status_code}")
            print(f"Pagination links: {devices.headers.get('Link')}")
            # print(f"{devices.text}")
            print("*"*40)
            if network.status_code == 200 and devices.status_code == 200:
                all_devices = get_all_devices(session, devices)
                print(f"Total devices: {len(all_devices)}")
                print("*"*40)
                for net in network.json():
                    if net["name"] == "branch_office":
                        show_unnamed_devices(all_devices, net["id"])
    else:
        print(org.text)