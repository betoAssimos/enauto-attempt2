import os
import requests
import urllib3
import json
import time
from dotenv import load_dotenv

# Initialize environment and remove certificate warning
load_dotenv(override=True)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables
BASE_URL = os.environ["SDWAN_HOST"]
USERNAME = os.environ["SDWAN_USERNAME"]
PASSWORD = os.environ["SDWAN_PASSWORD"]

def login(session):
    auth_payload = {
        "j_username": USERNAME,
        "j_password": PASSWORD
    }
    url = f"{BASE_URL}/j_security_check"
    r = session.post(url, data=auth_payload, timeout=30)
    r.raise_for_status()
    return r

def get_token(session):
    url = f"{BASE_URL}/dataservice/client/token"
    r = session.get(url, timeout=30)
    r.raise_for_status()
    return r

def get_devices(session):
    url = f"{BASE_URL}/dataservice/device"
    r = session.get(url, timeout=30)
    r.raise_for_status()
    return r.json()["data"]

def find_unhealthy(devices, min_control):
    flagged = []
    for device in devices:
        reasons = []
        if device.get("reachability") != "reachable":
            reasons.append("unreachable")
        if int(device.get("controlConnections") or 0) < min_control:
            reasons.append("control connections below threshold")
        if reasons:
            flagged.append({"host": device.get("host-name"), "reasons": reasons})
    return flagged

if __name__ == "__main__":
    with requests.Session() as session:
        session.verify = False
        session.headers.update({"Accept": "application/json"})

        # 1. Authenticate. A failed login still returns 200, but with an HTML page.
        login_response = login(session)
        if "<html" in login_response.text.lower():
            raise RuntimeError("SD-WAN login failed, check username and password.")

        token = get_token(session)
        session.headers["X-XSRF-TOKEN"] = token.text.strip()

        devices = get_devices(session)
        print(devices[0].keys())      
        for device in devices:
            print(device.get("host-name"), device.get("personality"), device.get("reachability"), device.get("status"), device.get("state"), repr(device.get("controlConnections")), repr(device.get("bfdSessions")))

        flagged = find_unhealthy(devices, min_control=4)
        if flagged:
            for item in flagged:
                print(f"UNHEALTHY {item['host']}: {', '.join(item['reasons'])}")
        else:
            print("All devices are healthy.")