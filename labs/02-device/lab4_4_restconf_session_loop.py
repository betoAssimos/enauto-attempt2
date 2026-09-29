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
# Using a SESSION to get the list of interfaces from another device using RESTCONF. This is used for persistent connections
devices = ["172.30.30.11", "172.30.30.12", "172.30.30.13"]
session = requests.Session()
session.auth = HTTPBasicAuth(user, pwd)
session.verify = False
session.headers.update(headers)

for device in devices:
    base_url = f"https://{device}/restconf/data/"
    conn = session.get(url=base_url+"ietf-interfaces:interfaces")
    print(f"\n=== {device} ===")
    print(f"Status Code: {conn.status_code}")
    interfaces = conn.json()["ietf-interfaces:interfaces"]["interface"]
    for interface in interfaces:
        print(interface["name"], interface.get("description", "<no description>"))