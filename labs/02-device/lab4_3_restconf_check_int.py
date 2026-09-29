import urllib3
import os
from dotenv import load_dotenv
import requests
from requests.auth import HTTPBasicAuth

urllib3.disable_warnings()
load_dotenv()

user = os.getenv("IOS_DEVICE_USER")
pwd = os.getenv("IOS_DEVICE_PASS")

# Using normal REQUESTS library to get the list of interfaces from two different devices using RESTCONF
host = "172.30.30.12"
base_url = f"https://{host}/restconf/data/"
headers = {"Accept": "application/yang-data+json", "Content-Type": "application/yang-data+json"}

response = requests.get(url=base_url+"ietf-interfaces:interfaces", auth=(user,pwd), headers=headers, verify=False)
data = response.json()

interfaces = data["ietf-interfaces:interfaces"]["interface"]
for interface in interfaces:
	print(interface["name"], interface.get("description", "<no description>"))

# Using a SESSION to get the list of interfaces from another device using RESTCONF. This is used for persistent connections
host_2 = "172.30.30.13"
base_url_2 = f"https://{host_2}/restconf/data/"
session = requests.Session()
session.auth = HTTPBasicAuth(user, pwd)
session.verify = False
session.headers.update(headers)
s = session.get(url=base_url_2+"ietf-interfaces:interfaces")
interfaces_2 = s.json()["ietf-interfaces:interfaces"]["interface"]
for interface in interfaces_2:
    print(interface["name"], interface.get("description", "<no description>"))


host_1 = "172.30.30.11"
base_url_1 = f"https://{host_1}/restconf/data/"
headers = {"Accept": "application/yang-data+json", "Content-Type": "application/yang-data+json"}

response = requests.get(url=base_url_1+"ietf-interfaces:interfaces", auth=(user,pwd), headers=headers, verify=False)
data = response.json()

interfaces = data["ietf-interfaces:interfaces"]["interface"]
for interface in interfaces:
	print(interface["name"], interface.get("description", "<no description>"))