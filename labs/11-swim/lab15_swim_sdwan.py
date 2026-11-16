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
    matches = []
    for image in images:
        if image.get("versionName") == target_version and image.get("versionType") == "vmanage":
            matches.append(image)

    if len(matches) != 1:
        raise ValueError("Expected exactly one matching version in the Manager repository.")

    return matches[0]

def install_image(session, device, target_version):
    url = f"{BASE_URL}/dataservice/device/action/install"
    # Local-repository payload used by the installed catalystwan SDK.
    # This write path has not been tested on this reservation.
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
        validation = task.get("validation") or {}

        if validation.get("status") in ("Failure", "Validation failure"):
            raise RuntimeError(f"Task validation failed: {validation}")

        results = task.get("data") or []
        for result in results:
            if result.get("statusId") == "failure" or result.get("status") == "Failure":
                raise RuntimeError(f"Task failed: {result}")

        # Empty results are not evidence of success.
        if results and all(
            result.get("statusId") == "success" or result.get("status") == "Success"
            for result in results
        ):
            return task

        time.sleep(interval)

    raise TimeoutError(f"Task {task_id} did not succeed after {max_attempts} attempts.")

def verify_upgrade(session, device_uuid, target_version, max_attempts=60, interval=10):
    for _ in range(max_attempts):
        try:
            devices = get_devices(session)
            for device in devices:
                if device.get("uuid") == device_uuid:
                    if device.get("reachability") == "reachable" and device.get("version") == target_version:
                        software = get_device_software(session, device["system-ip"])
                        for image in software:
                            if image.get("version") == target_version and str(image.get("active")).lower() == "true":
                                return device
                    break
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            pass

        time.sleep(interval)

    raise TimeoutError("Device did not return reachable with the target version active.")

if __name__ == "__main__":
    with requests.Session() as session:
        session.verify = False
        session.headers.update({"Accept": "application/json"})

        login_response = login(session)
        if "<html" in login_response.text.lower():
            raise RuntimeError("SD-WAN login returned an HTML page; check authentication.")

        token = get_token(session)
        session.headers["X-XSRF-TOKEN"] = token.text.strip()

        devices = get_devices(session)
        images = get_images(session)

        #print("DEVICES")
        #print(json.dumps(devices, indent=2))
        #print("SOFTWARE REPOSITORY")
        #print(json.dumps(images, indent=2))

        selected_device = None
        for device in devices:
            if device.get("host-name") == "Edge1":
                selected_device = device
                break

        if selected_device is None:
            raise ValueError("Device with hostname 'Edge1' not found.")

        software = get_device_software(session, selected_device["system-ip"])
        print(json.dumps(software, indent=2))

        # Write operations are disabled until a compatible image is available.
        apply_upgrade = False
        image_path = ""       # Optional: local .bin file to upload.
        target_version = ""   # Exact versionName returned by the repository.
        make_default = False

        if apply_upgrade:
            if not target_version:
                raise ValueError("Set target_version before enabling upgrades.")

            if selected_device.get("personality") != "vedge":
                raise ValueError("This workflow is restricted to an edge device.")

            if selected_device.get("reachability") != "reachable":
                raise ValueError("The selected device is not reachable.")

            if selected_device.get("version") == target_version:
                raise ValueError("The selected device is already running the target version.")

            original_version = selected_device["version"]

            if image_path:
                upload_result = upload_image(session, image_path)
                print(f"Upload HTTP status: {upload_result.status_code}")
                images = get_images(session)

            selected_image = select_image(images, target_version)
            print(json.dumps(selected_image, indent=2))

            install_task_id = install_image(session, selected_device, target_version)
            print(f"Installation task: {install_task_id}")
            install_task = wait_for_task(session, install_task_id)
            print(json.dumps(install_task, indent=2))

            # Confirm installation before requesting activation.
            software = get_device_software(session, selected_device["system-ip"])
            if not any(image.get("version") == target_version for image in software):
                raise RuntimeError("Installation finished but the target version is not listed on the device.")

            activate_task_id = activate_image(session, selected_device, target_version)
            print(f"Activation task: {activate_task_id}")
            activate_task = wait_for_task(session, activate_task_id)
            print(json.dumps(activate_task, indent=2))

            verified_device = verify_upgrade(session, selected_device["uuid"], target_version)
            print(f"Device: {verified_device['host-name']}, Before: {original_version}, After: {verified_device['version']}, Reachability: {verified_device['reachability']}")

            if make_default:
                default_task_id = set_default_image(session, selected_device, target_version)
                print(f"Default-version task: {default_task_id}")
                default_task = wait_for_task(session, default_task_id)
                print(json.dumps(default_task, indent=2))

                software = get_device_software(session, selected_device["system-ip"])
                if not any(
                    image.get("version") == target_version and str(image.get("default")).lower() == "true"
                    for image in software
                ):
                    raise RuntimeError("The target version was not reported as default.")

                print(f"Default version verified: {target_version}")