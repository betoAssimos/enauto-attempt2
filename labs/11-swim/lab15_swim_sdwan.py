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

def get_images(session):
    url = f"{BASE_URL}/dataservice/device/action/software"
    r = session.get(url, timeout=30)
    r.raise_for_status()
    return r.json()["data"]

def get_device_software(session, system_ip):
    url = f"{BASE_URL}/dataservice/device/software"
    params = {"deviceId": system_ip}
    r = session.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()["data"]

def upload_image(session, image_path):
    url = f"{BASE_URL}/dataservice/device/action/software/package"
    with open(image_path, "rb") as image_file:
        files = {"file": image_file}
        r = session.post(url, files=files, timeout=300)
        r.raise_for_status()
        return r

def select_image(images, target_version):
    for image in images:
        if image.get("versionName") == target_version and image.get("versionType") == "vmanage":
            return image
    raise ValueError(f"Version '{target_version}' not found in the Manager repository.")

def install_image(session, device, target_version):
    url = f"{BASE_URL}/dataservice/device/action/install"
    # NOT TESTED. versionType vmanage = image comes from the Manager repository.
    payload = {
        "action": "install",
        "input": {
            "vEdgeVPN": 0,
            "vSmartVPN": 0,
            "family": "vedge",
            "version": target_version,
            "versionType": "vmanage",
            "reboot": False,
            "sync": True
        },
        "devices": [{
            "deviceIP": device["system-ip"],
            "deviceId": device["uuid"]
        }],
        "deviceType": "vedge"
    }
    r = session.post(url, json=payload, timeout=30)
    r.raise_for_status()
    return r.json()["id"]

def activate_image(session, device, target_version):
    url = f"{BASE_URL}/dataservice/device/action/changepartition"
    payload = {
        "action": "changepartition",
        "devices": [{
            "version": target_version,
            "deviceIP": device["system-ip"],
            "deviceId": device["uuid"]
        }],
        "deviceType": "vedge"
    }
    r = session.post(url, json=payload, timeout=30)
    r.raise_for_status()
    return r.json()["id"]

def set_default_image(session, device, target_version):
    url = f"{BASE_URL}/dataservice/device/action/defaultpartition"
    payload = {
        "action": "defaultpartition",
        "devices": [{
            "version": target_version,
            "deviceIP": device["system-ip"],
            "deviceId": device["uuid"]
        }],
        "deviceType": "vedge"
    }
    r = session.post(url, json=payload, timeout=30)
    r.raise_for_status()
    return r.json()["id"]

def get_task(session, task_id):
    url = f"{BASE_URL}/dataservice/device/action/status/{task_id}"
    r = session.get(url, timeout=30)
    r.raise_for_status()
    return r.json()

def wait_for_task(session, task_id, max_attempts=180, interval=10):
    for _ in range(max_attempts):
        task = get_task(session, task_id)
        results = task.get("data") or []

        for result in results:
            if result.get("statusId") == "failure":
                raise RuntimeError(f"Task failed: {result}")

        # Empty data means the task did not report yet, keep waiting.
        done = 0
        for result in results:
            if result.get("statusId") == "success":
                done += 1
        if results and done == len(results):
            return task

        time.sleep(interval)
    raise TimeoutError(f"Task {task_id} did not complete after {max_attempts} attempts.")

def verify_upgrade(session, device_uuid, target_version, max_attempts=60, interval=10):
    # Task success is not enough, check what the device reports after the reboot.
    for _ in range(max_attempts):
        for device in get_devices(session):
            if device.get("uuid") == device_uuid:
                if device.get("reachability") == "reachable" and device.get("version") == target_version:
                    return device
        time.sleep(interval)
    raise TimeoutError("Device did not come back reachable on the target version.")

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

        # 2. Inventory and repository
        devices = get_devices(session)
        images = get_images(session)
        print(f"Count of images in repository: {len(images)}")

        selected_device = None
        for device in devices:
            print(f"Hostname: {device.get('host-name')}, Version: {device.get('version')}, Reachability: {device.get('reachability')}")
            if device.get("host-name") == "Edge1":
                selected_device = device
        if selected_device is None:
            raise ValueError("Device with hostname 'Edge1' not found.")

        # 3. Software installed on Edge1
        software = get_device_software(session, selected_device["system-ip"])
        print(json.dumps(software, indent=2))

        # 4. Upgrade - NOT TESTED, no compatible image for this reservation.
        # Order: upload -> install -> activate -> verify -> set default
        apply_upgrade = False
        image_path = ""
        target_version = ""
        make_default = False

        if apply_upgrade:
            if selected_device.get("version") == target_version:
                raise ValueError("Edge1 is already running the target version.")
            original_version = selected_device["version"]

            if image_path:
                upload_image(session, image_path)
                images = get_images(session)

            selected_image = select_image(images, target_version)
            print(f"Selected image: {selected_image['versionName']}")

            install_task_id = install_image(session, selected_device, target_version)
            wait_for_task(session, install_task_id)

            activate_task_id = activate_image(session, selected_device, target_version)
            wait_for_task(session, activate_task_id)

            verified = verify_upgrade(session, selected_device["uuid"], target_version)
            print(f"Device: {verified['host-name']}, Before: {original_version}, After: {verified['version']}")

            if make_default:
                default_task_id = set_default_image(session, selected_device, target_version)
                wait_for_task(session, default_task_id)