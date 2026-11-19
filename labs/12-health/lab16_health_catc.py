import os

import requests
import urllib3
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv(override=True)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = os.environ["CATC_BASE_URL"]
USERNAME = os.environ["CATC_USERNAME"]
PASSWORD = os.environ["CATC_PASSWORD"]

#################### FUNCTIONS #########################
def get_token(session):
    """Get a token from the Catalyst Center API."""
    url = f"{BASE_URL}/dna/system/api/v1/auth/token"
    r = session.post(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), timeout=30)
    r.raise_for_status()
    return r.json()["Token"]

def get_site_health(session):
     """Get the health for all sites from CATC API."""
     url = f"{BASE_URL}/dna/intent/api/v1/site-health"
     r = session.get(url, timeout=30)
     r.raise_for_status()
     return r.json()["response"]

def get_device_health(session):
     """ Get the health for all devices."""
     url = f"{BASE_URL}/dna/intent/api/v1/device-health"
     r = session.get(url, timeout=30)
     r.raise_for_status()
     return r.json()["response"]

def get_device_list(session):
    url = f"{BASE_URL}/dna/intent/api/v1/network-device"
    resp = session.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()["response"]

#################### HELPERS #########################
def find_unreachable(devices, expected):
    """Find devicces unreachable."""
    flagged = []
    for device in devices:
        status = device.get("reachabilityStatus")
        if status != expected:
             flagged.append({"device": device.get("hostname"), "status": status})
    return flagged

if __name__ == "__main__":
        with requests.Session() as session:
            session.verify = False
            session.headers.update({"Accept": "application/json"})
            token = get_token(session)
            session.headers.update({"X-Auth-Token": token, "Content-Type": "application/json"})
            #print("token length:", len(token))
            #site_health = get_site_health(session)
            #print("site health hit 1 top-level keys:", list(site_health[0].keys()))
            #for site in site_health:
                 #print(site.get("siteName"), repr(site.get("numberOfNetworkDevice")), repr(site.get("healthyNetworkDevicePercentage")), repr(site.get("overallGoodDevices")))

            inventory = get_device_list(session)
            # test: empty inventory branch
            #inventory = []
            for device in inventory:
                 print(device.get("hostname"))
            # test: expected Up
            #flagged = find_unreachable(inventory, "Up")
            flagged = find_unreachable(inventory, "Reachable")
            if not inventory:
                 print("No devices in inventory")
            elif flagged:
                print("Devices unreachable:")
                for device in flagged:
                    print(device)
            else:
                print("All devices are reachable.")