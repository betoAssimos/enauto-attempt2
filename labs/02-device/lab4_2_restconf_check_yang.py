import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import urllib3
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

user = os.getenv("IOS_DEVICE_USER")
pwd = os.getenv("IOS_DEVICE_PASS")

host = "172.30.30.11"
base_url = f"https://{host}/restconf/data/"
headers = {"Accept": "application/yang-data+json", "Content-Type": "application/yang-data+json"}

response = requests.get(url=base_url+"ietf-yang-library:modules-state", auth=(user,pwd), headers=headers, verify=False)
data = response.json()

modules = data["ietf-yang-library:modules-state"]["module"]

for module in modules:
    # print(module["name"])
    if "ospf" in module["name"].lower():
        print(module["name"])
