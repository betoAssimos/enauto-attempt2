import os
import time
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

def get_token(session):
    url = f"{BASE_URL}{AUTH_PATH}"
    resp = session.post(url, auth=HTTPBasicAuth(USERNAME, PASSWORD))
    resp.raise_for_status()
    token = resp.json()["Token"]
    return token

def get_device_list(session):
    url = f"{BASE_URL}/dna/intent/api/v1/network-device"
    resp = session.get(url)
    resp.raise_for_status()
    return resp.json()["response"]

def get_sf_img(session):
    url = f"{BASE_URL}/dna/intent/api/v1/image/importation"
    resp = session.get(url)
    resp.raise_for_status()
    return resp.json()["response"]

def distribute_image(session, device_id, image_id):
    url = f"{BASE_URL}/dna/intent/api/v1/image/distribution"
    payload = [{
        "deviceUuid": device_id,
        "imageUuid": image_id
    }]
    resp = session.post(url, json=payload)
    resp.raise_for_status()
    return resp.json()["response"]

def import_image(session, source_url):
    url = f"{BASE_URL}/dna/intent/api/v1/image/importation/source/url"
    payload = [{"sourceURL": source_url, "thirdParty": False}]
    resp = session.post(url, json=payload)
    resp.raise_for_status()
    return resp.json()["response"]

def get_task(task_id, session):
    url = f"{BASE_URL}/dna/intent/api/v1/task/{task_id}"
    r = session.get(url)
    r.raise_for_status()
    return r.json()["response"]

def wait_for_task(task_id, session, max_attempts=30, interval=2):
    for _ in range(max_attempts):
        task = get_task(task_id, session)
        if task.get("endTime"):
            if task.get("isError"):
                raise RuntimeError(task.get("failureReason") or task.get("progress") or "Task failed")
            return task
        time.sleep(interval)
    raise TimeoutError(f"Task {task_id} did not complete after {max_attempts} attempts.")

def activate_image(session, device_id, image_id):
    url = f"{BASE_URL}/dna/intent/api/v1/image/activation/device"
    payload = [{"deviceUuid": device_id, "imageUuidList": [image_id]}]
    resp = session.post(url, json=payload)
    resp.raise_for_status()
    return resp.json()["response"]

def select_image(image_list, image_name):
    for image in image_list:
        if image.get("name") == image_name:
            return image["imageUuid"]
    raise ValueError(f"Image with name '{image_name}' not found in the list.")

if __name__ == "__main__":
    with requests.Session() as session:
        session.verify = False
        token = get_token(session)
        #print(f"Token: {token}")
        session.headers.update({"X-Auth-Token": token, "Content-Type": "application/json"})
        device_list = get_device_list(session)
        #print(f"Device List: {device_list}")
        device_id = None
        for device in device_list:
            print(f"Device ID: {device['id']}, Hostname: {device['hostname']}, Software Version: {device['softwareVersion']}, Platform ID: {device['platformId']}")
            if device.get("hostname") == "sw1":
                device_id = device['id']
        if device_id is None:        
            raise ValueError("Device with hostname 'sw1' not found.")
        
        print(f"Selected device: sw1, ID: {device_id}")

        image_list = get_sf_img(session)
        print(f"Count of Software Images: {len(image_list)}")

        if image_list:
            image_id = select_image(image_list, "test-image.bin")
            print(f"Selected image: {image_id}")
        else:
            print(f"No software images returned by Catalyst Center.")

        #imgdist_task = distribute_image(session, device_id, image_id)
        #import_result = import_image(session, "http://swim-lab.invalid/test-image.bin")
        #task_id = import_result['taskId']
        #task_result = wait_for_task(task_id, session)

        #print("End time:", task_result.get("endTime"))
        #print("Is error:", task_result.get("isError"))
        #print("Progress:", task_result.get("progress"))
        #print("Failure reason:", task_result.get("failureReason"))
        #imgdist_task = distribute_image(session, device_id, image_id)
        #wait_for_task(imgdist_task["taskId"], session)
        #activate_result = activate_image(session, device_id, image_id)
        #wait_for_task(activate_result["taskId"], session)
