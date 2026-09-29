import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import os
import urllib3


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

username = os.environ.get("IOS_DEVICE_USER")
password = os.environ.get("IOS_DEVICE_PASS")

url = "https://172.30.30.11/restconf/data/ietf-interfaces:interfaces"

session = requests.Session()

session.auth = HTTPBasicAuth(username, password)
session.verify = False
session.headers.update({
    "Accept": "application/yang-data+json",
})
# Verify first before doing anything
response = session.get(url)

#print(f"Status Code: {response.status_code}")
#print(f"Response Body: {response.text}")

payload = {
    "ietf-interfaces:interface": {
        "name": "GigabitEthernet1",
        "description": "Configured via RESTCONF API",
    }
}
#Apply the PATCH request to update a config
session.headers.update({
    "Content-Type": "application/yang-data+json",
})

target_uri = f"{url}/interface=GigabitEthernet1"
#print("="*40)
#response = session.patch(target_uri, json=payload)
#print(f"Status Code: {response.status_code}")
#print(f"Response Body: {response.text}")

#Verify once more after the PATCH
#print("="*40)
response = session.get(url)
#print(f"Status Code: {response.status_code}")
#print(f"Response Body: {response.text}")

# Creating a resource
payload = {
    "ietf-interfaces:interface": {
        "name": "Loopback99",
        "description": "Created via RESTCONF API",
        "type": "iana-if-type:softwareLoopback",
        "enabled": True,
    }
}

# Apply the POST request to create a new resource
#print("="*40)
response = session.post(url, json=payload)
#print(f"Status Code: {response.status_code}")
#print(f"Response Body: {response.text}")

#Verify once more after the POST
#print("="*40)
response = session.get(f"{url}/interface=Loopback99")
#print(f"Status Code: {response.status_code}")
#print(f"Response Body: {response.text}")

ip_payload = {
    "ietf-interfaces:interface": {
        "name": "Loopback99",
        "ietf-ip:ipv4": {
            "address": [
                {
                    "ip": "192.0.2.100",
                    "netmask": "255.255.255.255"
                }
            ]
        }
    }
}
# Apply the PATCH request to update the IP address of the Loopback99 interface
#print("="*40)
response = session.patch(f"{url}/interface=Loopback99", json=ip_payload)
#print(f"Status Code: {response.status_code}")
#print(f"Response Body: {response.text}")

#response = session.get(f"{url}/interface=Loopback99")
#print(f"Response Body: {response.text}")

#print("="*40)
#delete_uri = f"{url}/interface=Loopback99/ietf-ip:ipv4/address=192.0.2.101"
#response = session.delete(delete_uri)
#print(f"Status Code: {response.status_code}")
#print(f"Response Body: {response.text}")

#print("="*40)
#response = session.get(f"{url}/interface=Loopback99")
#print(f"Response Body: {response.text}")
# Delete interface
#print("="*40)
#delete_lb = f"{url}/interface=Loopback99"
#response = session.delete(delete_lb)
#print(f"Status Code: {response.status_code}")
#print(f"Response Body: {response.text}")

#print("="*40)
response = session.get(f"{url}/interface=Loopback99")
#print(f"Status Code: {response.status_code}")
#print(f"Response Body: {response.text}")

put_payload = {
    "ietf-interfaces:interface": {
        "name": "Loopback99",
        "type": "iana-if-type:softwareLoopback",
        "enabled": True
    }
}

#print("="*40)
#response = session.put(f"{url}/interface=Loopback99", json=put_payload)
#print(f"Status Code: {response.status_code}")
#print(f"Response Body: {response.text}")

print("="*40)
response = session.get(f"{url}/interface=Loopback99")
print(f"Status Code: {response.status_code}")
print(f"Response Body: {response.text}")

# =========================================================
# STEP 8: Handle Invalid Requests (Phase C — Break Tests)
# =========================================================

# 8a. Trigger 415 Unsupported Media Type (Passing plain application/json)
print("="*40)
print("Testing 415 Unsupported Media Type...")
bad_headers = {"Content-Type": "application/json"}
response = session.patch(f"{url}/interface=GigabitEthernet1", json=payload, headers=bad_headers)
print(f"Status Code: {response.status_code}")
print(f"Response Body: {response.text}")

# 8b. Trying POST on already created resource
print("="*40)
print("Testing 409 Conflict (POST on existing resource)...")
response = session.post(f"{url}", json=payload)
print(f"Status Code: {response.status_code}")
print(f"Response Body: {response.text}")