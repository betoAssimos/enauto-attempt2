import os
import requests
import json
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

load_dotenv(override=True)

BASE_URL = "https://api.meraki.com/api/v1"
API_KEY = os.environ["MERAKI_API_KEY"]

def get_org(session):
    url = f"{BASE_URL}/organizations"
    r = session.get(url, timeout=30)
    r.raise_for_status()
    return r.json()

def get_networks(session, org_id):
    url = f"{BASE_URL}/organizations/{org_id}/networks"
    r = session.get(url, timeout=30)
    r.raise_for_status()
    return r.json()

def get_upgrades(session, network_id):
    url = f"{BASE_URL}/networks/{network_id}/firmwareUpgrades"
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

def schedule_firmware(session, network_id, product_type, version_id, upgrade_time):
    url = f"{BASE_URL}/networks/{network_id}/firmwareUpgrades"
    payload = {
        "products": {
            product_type: {
                "nextUpgrade": {
                    "time": upgrade_time,
                    "toVersion": {
                        "id": version_id
                    }
                }
            }
        }
    }
    r = session.put(url, json=payload, timeout=30)
    r.raise_for_status()
    return r.json()

if __name__ == "__main__":
    with requests.Session() as session:
        session.headers.update({
            "X-Cisco-Meraki-API-Key": API_KEY,
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

        for network in networks:
            print(f"Network ID: {network['id']}, Name: {network['name']}, Type: {network['productTypes']}")
        
        firmware_upgrades = get_upgrades(session, network_id)
        #print(json.dumps(firmware_upgrades, indent=4))
        devices = get_devices(session, network_id)
        #print(json.dumps(devices, indent=4))
        availability = get_device_availability(session, org_id, network_id)
        #print(json.dumps(availability, indent=4))
        apply_upgrade = False

        if apply_upgrade:
            product_type = "switch"
            switch_firmware = firmware_upgrades["products"][product_type]

            available_ids = []
            for version in switch_firmware["availableVersions"]:
                print(f"{version['id']} | {version['shortName']} | {version['releaseType']}")
                available_ids.append(version["id"])

            version_id = input("Enter the target firmware ID: ").strip()

            if version_id not in available_ids:
                raise ValueError("The selected firmware ID is not listed as available.")

            if version_id == switch_firmware["currentVersion"]["id"]:
                raise ValueError("The selected version is already configured.")

            upgrade_time = (datetime.now(timezone.utc) + timedelta(minutes=10)
            ).strftime("%Y-%m-%dT%H:%M:%SZ")

            try:
                result = schedule_firmware(session, network_id, product_type, version_id, upgrade_time)
            except requests.exceptions.HTTPError as exc:
                #print(f"Meraki returned HTTP {exc.response.status_code}")
                #print(exc.response.text)
                raise

            print(json.dumps(result, indent=4))

            updated = get_upgrades(session, network_id)
            print(json.dumps(updated["products"][product_type]["nextUpgrade"], indent=4))