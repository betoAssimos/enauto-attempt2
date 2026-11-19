import os
import requests
import json
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

load_dotenv(override=True)

BASE_URL = os.environ["MERAKI_HOST"]
API_KEY = os.environ["MERAKI_API_KEY"]
print(len(API_KEY), API_KEY[:4])

def get_org(session):
    url = f"{BASE_URL}/organizations"
    r = session.get(url, timeout=30)
    print(r.status_code, r.text)
    print(r.status_code, r.url, r.history, r.text)
    r.raise_for_status()
    return r.json()

def get_networks(session, org_id):
    url = f"{BASE_URL}/organizations/{org_id}/networks"
    r = session.get(url, timeout=30)
    r.raise_for_status()
    return r.json()

def get_devices(session, network_id):
    url = f"{BASE_URL}/networks/{network_id}/devices"
    r = session.get(url, timeout=30)
    r.raise_for_status()
    return r.json()

def get_device_availability(session, org_id, network_id):
    url = f"{BASE_URL}/organizations/{org_id}/devices/availabilities"
    params = {"networkIds[]": [network_id]}
    r = session.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

if __name__ == "__main__":
    with requests.Session() as session:
        session.headers.update({
            "Authorization": f"Bearer {API_KEY}",
            #"X-Cisco-Meraki-API-Key": API_KEY,
            "Content-Type": "application/json",
        })
        orgs = get_org(session)
        if len(orgs) != 1:
            raise ValueError("Expected exactly one organization for this reservation.")

        org_id = orgs[0]["id"]
        networks = get_networks(session, org_id)
        if len(networks) != 1:
            raise ValueError("Expected exactly one network for this reservation.")
        network_id = networks[0]["id"]
