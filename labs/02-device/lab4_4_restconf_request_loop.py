import urllib3
import os
from dotenv import load_dotenv
import requests
from requests.auth import HTTPBasicAuth

urllib3.disable_warnings()
load_dotenv()

user = os.getenv("IOS_DEVICE_USER")
pwd = os.getenv("IOS_DEVICE_PASS")

headers = {"Accept": "application/yang-data+json", "Content-Type": "application/yang-data+json"}
# Using a REQUEST to get the list of interfaces from another device using RESTCONF.
# No session object reuse
devices = ["172.30.30.11", "172.30.30.12", "172.30.30.13"]
for device in devices:
    base_url = f"https://{device}/restconf/data/"
    conn = requests.get(
        url=base_url+"ietf-interfaces:interfaces",
        headers=headers,
        auth=(user, pwd),
        verify=False
    )
    print(f"\n=== {device} ===")
    print(f"Status Code: {conn.status_code}")
    data =  conn.json()
    interfaces = data["ietf-interfaces:interfaces"]["interface"]
    for interface in interfaces:
        print(interface["name"], interface.get("description", "<no description>"))