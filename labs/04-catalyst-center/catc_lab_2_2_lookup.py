import os
import requests
import urllib3
import json
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from dnacentersdk import DNACenterAPI

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = os.environ["CATC_BASE_URL"]
USERNAME = os.environ["CATC_USERNAME"]
PASSWORD = os.environ["CATC_PASSWORD"]
AUTH_PATH = "/dna/system/api/v1/auth/token"

url = f"{BASE_URL}{AUTH_PATH}"
resp = requests.post(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), verify=False)
token = resp.json()["Token"]
headers = {"X-Auth-Token": token}

device_url = f"{BASE_URL}/dna/intent/api/v1/network-device"

def build_client():
    """Build a DNACenterAPI client."""
    api = DNACenterAPI(username=USERNAME, password=PASSWORD, base_url=BASE_URL, verify=False)
    return api

def fetch(params=None):
    r = requests.get(device_url, headers=headers, params=params, verify=False)
    return r.json()["response"]

baseline1 = fetch()
print("-------------------------------------------------------")
print("------------------------ID RAW-------------------------")
device_id = baseline1[1]["id"]
r = requests.get(f"{device_url}/{device_id}", headers=headers, verify=False)
print(r.status_code)
print(list(r.json().keys()))
print(type(r.json()["response"]))

print("-------------------------------------------------------")
print("--------------------ID SDK-----------------------------")
api = build_client()
r = api.devices.get_device_by_id(id=device_id)
print(list(r.keys()))
print(type(r))
print(type(r.response))

print("-------------------------------------------------------")
print("--------------------IP RAW-----------------------------")
device_ip = baseline1[1]["managementIpAddress"]
r = requests.get(f"{device_url}/ip-address/{device_ip}", headers=headers, verify=False)
print(r.json()["response"])

print("-------------------------------------------------------")
print("--------------------IP SDK-----------------------------")
api = build_client()
r = api.devices.get_network_device_by_ip(ip_address=device_ip)
print(r.response)

print("-------------------------------------------------------")
print("--------------------SERIAL RAW-------------------------")
device_serial = baseline1[1]["serialNumber"]
r = requests.get(f"{device_url}/serial-number/{device_serial}", headers=headers, verify=False)
#print(r.json()["response"])
print("baseline1:", [d["hostname"] for d in baseline1], "serial number: ", [d["serialNumber"] for d in baseline1])
print("--------------------ERROED SERIAL RAW-------------------")
r = requests.get(f"{device_url}/serial-number/bullshit", headers=headers, verify=False)
print(r.status_code)
print(r.json()["response"])

print("-------------------------------------------------------")
print("--------------------SERIAL SDK-------------------------")
api = build_client()
r = api.devices.get_device_by_serial_number(serial_number=device_serial)
print(r.response)
print("--------------------ERROED SERIAL SDK-------------------")
#r = api.devices.get_device_by_serial_number(serial_number="bullshit")
#print(r.response)


print("-------------------------------------------------------")
print("--------------------FILTER RAW-------------------------")
print("--------------------FAMILY-------------------------")
family = "Switches and Hubs"
r = requests.get(device_url, headers=headers, params={"notAPAraMeterdfj": family}, verify=False)
print(r.status_code, len(r.json()["response"]))

print("--------------------WRONG FAMILY-------------------------")
family = "wronggggg"
r = requests.get(device_url, headers=headers, params={"family": family}, verify=False)
print(r.status_code, len(r.json()["response"]))

print("--------------------ROLE-------------------------")
family = "Switches and Hubs"
role = "ACCESS"
r = requests.get(device_url, headers=headers, params={"family": family, "role": role}, verify=False)
print(r.status_code, len(r.json()["response"]))

print("--------------------WRONG ROLE-------------------------")
role = "wronggggg"
r = requests.get(device_url, headers=headers, params={"family": family, "role": role}, verify=False)
print(r.status_code, len(r.json()["response"]))

print("--------------------SOFTWARE VERSION-------------------------")
family = "Switches and Hubs"
role = "ACCESS"
swver = "17.12.1prd9"
r = requests.get(device_url, headers=headers, params={"family": family, "role": role, "softwareVersion": swver}, verify=False)
print(r.status_code, len(r.json()["response"]))

print("--------------------WRONG SOFTWARE VERSION-------------------------")
swver = "wronggggg"
r = requests.get(device_url, headers=headers, params={"family": family, "role": role,"softwareVersion": swver}, verify=False)
print(r.status_code, len(r.json()["response"]))

print("--------------------FILTER SDK-------------------------")
print("--------------------FAMILY-------------------------")
api = build_client()
family = "Switches and Hubs"
role = "ACCESS"
swver = "17.12.1prd9"
r = api.devices.get_device_list(family=family)
print(len(r.response))

print("--------------------ROLE-------------------------")
r = api.devices.get_device_list(family=family, role=role)
print(len(r.response))

print("--------------------SOFTWARE VERSION-------------------------")
r = api.devices.get_device_list(family=family, role=role, softwareVersion=swver)
print(len(r.response))

print("--------------------WRONG FAMILY-------------------------")
family = "wronggggg"
r = api.devices.get_device_list(family=family)
print(len(r.response))

print("--------------------WRONG ROLE-------------------------")
family = "Switches and Hubs"
role = "wronggggg"
r = api.devices.get_device_list(family=family, role=role)
print(len(r.response))

print("--------------------WRONG SOFTWARE VERSION-------------------------")
family = "Switches and Hubs"
role = "ACCESS"
swver = "wronggggg"
r = api.devices.get_device_list(family=family, role=role, softwareVersion=swver)
print(len(r.response))