import requests
import json
from requests.auth import HTTPBasicAuth
import urllib3
from ncclient import manager
urllib3.disable_warnings()

#- wrong namespace
#- wrong hierarchy
#- wrong leaf name
#- configuration/state confusion

device = manager.connect(
    host="172.30.30.11",
    port=830,
    username="admin",
    password="admin",
    hostkey_verify=False,
    device_params={"name": "iosxe"}
)
filter_intf = """
<interface xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
	<named>Loopback1</named>
</interface>
"""
reply = device.get_config(source="running", filter=("subtree", filter_intf))
#print(reply.xml)

print("-----------------------------------------------------------------")
config = """
<config>
	<interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
		<interface>
			<name>Loopback1</name>
			<description>Test</description>
			<type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:softwareLoopback</type>
			<enabled>true</enabled>
            <oper-status>up</oper-status>
		</interface>
	</interfaces>
</config>
"""
#print((device.edit_config(target="running", config=config)).xml)



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

payload = {
	"ietf-interfaces:interface":
			{
				"name": "Loopback2",
				"descriptions": "Test",
				"type": "iana-if-type:softwareLoopback",
				"enabled": True,
			}
}

s = requests.Session()
s.auth = auth
s.headers.update(headers)
s.verify = False
r = s.put(f"{base_url}/ietf-interfaces:interfaces/interface=Loopback2", data=json.dumps(payload))
print(f"[create] -> {r.status_code}  (201=created, 204=replaced)")
print(r.text)