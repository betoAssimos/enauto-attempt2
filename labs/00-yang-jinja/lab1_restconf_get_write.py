import requests
import json
from requests.auth import HTTPBasicAuth
import urllib3
urllib3.disable_warnings()

base_url = "https://172.30.30.11:443/restconf/data"
auth = HTTPBasicAuth("admin","admin")
headers = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json"
}
s = requests.Session()
s.auth = auth
s.headers.update(headers)
s.verify = False
r = s.get(f"{base_url}/ietf-interfaces:interfaces/interface=Loopback2")
print(f"[verify] -> {r.status_code}  (200=present, 404=absent)")
if r.text: print(r.text)

interface = "Loopback2"
interface_url = f"{base_url}/ietf-interfaces:interfaces/interface={interface}"

payload = {
	"ietf-interfaces:interface":
			{
				"name": interface,
				"description": "Test",
				"type": "iana-if-type:softwareLoopback",
				"enabled": True
			}
}

s = requests.Session()
s.auth = auth
s.headers.update(headers)
s.verify = False
r = s.put(interface_url, data=json.dumps(payload))
print(f"[create] -> {r.status_code}  (201=created, 204=replaced)")
print(r.text)

s = requests.Session()
s.auth = auth
s.headers.update(headers)
s.verify = False
r = s.get(f"{base_url}/ietf-interfaces:interfaces/interface=Loopback2")
print(f"[verify] -> {r.status_code}  (200=present, 404=absent)")
if r.text: print(r.text)