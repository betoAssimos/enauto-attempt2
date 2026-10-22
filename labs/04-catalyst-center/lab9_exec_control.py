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
    """Get an authentication token from Catalyst Center API"""
    AUTH_PATH = "/dna/system/api/v1/auth/token"
    url=f"{BASE_URL}{AUTH_PATH}"
    resp = requests.post(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), verify=False)
    resp.raise_for_status()
    return resp.json()["Token"]

def get_device_list(headers):
    """Get a list of network devices from DNAC"""
    device_url = "/dna/intent/api/v1/network-device"
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

def run_command(headers, payload):
    url = f"{BASE_URL}/dna/intent/api/v1/network-device-poller/cli/read-request"
    r = requests.post(url, headers=headers, json=payload, verify=False)
    print(f"{r.status_code}")
    r.raise_for_status()
    return r.json()

def get_cmd_output(headers, file_id):
    file_url = f"{BASE_URL}/dna/intent/api/v1/file/{file_id}"
    r = requests.get(file_url, headers=headers, verify=False)
    r.raise_for_status()
    return r.json()

if __name__ == "__main__":
    TOKEN = get_token()
    new_headers = {"X-Auth-Token": TOKEN, "Content-Type": "application/json"}
    print("Authenticated; token lenght:", len(TOKEN))
    devices = get_device_list(new_headers)
    #print("Top-level type:", type(devices))
    #print("Top-level keys:", devices.keys())

    #print("Response type:", type(devices["response"]))
    print("Device count:", len(devices["response"]))
    #first_device = devices["response"][0]
    #print(first_device.get("locationName", "Unknown"))
    #print(first_device.get("invalidField", "Unknown"))
    #print(first_device["invalidField"])
    #for device in devices["response"]:
    #print(f"Hostname: {device["hostname"]} | IP: {device["managementIpAddress"]} | Status: {device["reachabilityStatus"]} | ID: {device["id"]}")

    #for device in devices["response"]:
    #    if device["reachabilityStatus"] == "Unreachable":
    #        print(f"Hostname: {device["hostname"]} | IP: {device["managementIpAddress"]}")

    selected_ids = []

    for device in devices["response"]:
        if device["hostname"] == "sw1" and device["reachabilityStatus"] == "Reachable":
            selected_ids.append(device["id"])

    print(f"Selected ID from SW1: {selected_ids}")
    print(type(selected_ids))
    print(type(selected_ids[0]))

    print(selected_ids)
    print([selected_ids])
    payload = {
        "commands": ["show running-config interface Vlan1"],
        "deviceUuids": selected_ids
    }

    print("##########################")
    cmd_run =  run_command(new_headers, payload)
    #print(json.dumps(cmd_run, indent=2))
    task_id = cmd_run["response"]["taskId"]
    print("##########################")
    print(task_id)
    print("##########################")
    task_result = wait_for_task(task_id, new_headers)
    #print(json.dumps(task_result, indent=2))
    file_id = json.loads(task_result["progress"])["fileId"]
    progress = get_cmd_output(new_headers, file_id)
    # print(json.dumps(progress, indent=2))
    responses = progress[0]["commandResponses"]

    failure = responses["FAILURE"]
    blocked = responses["BLOCKLISTED"]
    success = responses["SUCCESS"]

    if failure or blocked:
        raise RuntimeError(f"Failure: {failure} | Blocklisted: {blocked}")

    if "show running-config interface Vlan1" not in success:
        raise RuntimeError("show running-config interface Vlan1 missing from SUCCESS")

    cli_output = success["show running-config interface Vlan1"]
    print(cli_output)