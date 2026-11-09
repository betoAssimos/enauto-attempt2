import os
import requests
import urllib3
import json
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from ciscoisesdk import IdentityServicesEngineAPI
from catalystwan.session import create_manager_session

# Initialize environment and remove certificate warning
load_dotenv()
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
    r = session.post(url, data=auth_payload, verify=False)
    return r

def get_token(session):
    url = f"{BASE_URL}/dataservice/client/token"
    r = session.get(url, verify=False)
    return r

def get_device(session, hostname):
    r = session.get(f"{BASE_URL}/dataservice/system/device/vedges")

    for device in r.json()["data"]:
        if device.get("host-name") == hostname:
            return device


def get_group(session, group_id):
    r = session.get(f"{BASE_URL}/dataservice/v1/config-group/{group_id}")
    return r.json()


def get_system_profile(group):
    for profile in group["profiles"]:
        if profile["type"] == "system":
            return profile


def get_banners(session, system_id):
    url = f"{BASE_URL}/dataservice/v1/feature-profile/sdwan/system/{system_id}/banner"
    r = session.get(url)
    return r.json()

def create_banner(session, system_id):
    url = f"{BASE_URL}/dataservice/v1/feature-profile/sdwan/system/{system_id}/banner"
    payload = {
        "name": "ENAUTO_LAB14_BANNER",
        "data": {
            "login": {"optionType": "global", "value": "ENAUTO LAB14"},
            "motd": {"optionType": "default", "value": ""}
        }
    }
    r = session.post(url, json=payload)
    return r

def deploy_group(session, group_id, device_uuid):
    url = f"{BASE_URL}/dataservice/v1/config-group/{group_id}/device/deploy"
    payload = {"devices": [{"id": device_uuid}]}
    r = session.post(url, json=payload)
    return r

def get_task(session, task_id):
    url = f"{BASE_URL}/dataservice/device/action/status/{task_id}"
    r = session.get(url)
    return r.json()

def get_running_config(session, system_ip):
    url = f"{BASE_URL}/dataservice/device/config?deviceId={system_ip}"
    r = session.get(url, headers={"Accept": "text/plain"})
    return r

def get_devices_sdk(session):
    devices = session.api.devices.get()
    return devices

# Start
if __name__ == "__main__":
    # 1. Authenticate
    session = requests.Session()
    session.headers.update({"Accept": "application/json"})
    session.verify = False

    resp = login(session)
    token = get_token(session)
    session.headers["X-XSRF-TOKEN"] = token.text

    # 2. Discover device -> group -> system profile
    device = get_device(session, "Edge1")
    group = get_group(session, device["id"])
    profile = get_system_profile(group)

    # 3. Create banner and verify it in Manager — completed
    # banners = get_banners(session, profile["id"])
    # if banners["data"] == []:
    #     created = create_banner(session, profile["id"])
    #     print(created.status_code)
    #     print(created.text)
    #
    # banners = get_banners(session, profile["id"])
    # print(json.dumps(banners, indent=2))

    # 4. Deploy configuration group to Edge1 — completed
    # deployment = deploy_group(session, group["id"], device["uuid"])
    # print(deployment.status_code)
    # print(deployment.text)
    # task_id = deployment.json()["parentTaskId"]

    # 5. Check deployment task — completed
    # task = get_task(session, task_id)
    # print(json.dumps(task["summary"], indent=2))

    # 6. Read back Edge1's running configuration — current step
    config = get_running_config(session, device["system-ip"])
    print(config.status_code)

    for line in config.text.splitlines():
        if "banner" in line or "ENAUTO LAB14" in line:
            print(line)

    sdk_session = create_manager_session(url=BASE_URL, username=USERNAME, password=PASSWORD)
    devices = get_devices_sdk(sdk_session)
    print("SDK devices:", len(devices))
    for sdk_device in devices:
        print(sdk_device.hostname)
    sdk_session.close()