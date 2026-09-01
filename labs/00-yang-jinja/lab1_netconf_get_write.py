from ncclient import manager
import xml.etree.ElementTree as ET

device = manager.connect(
    host="172.30.30.11",
    port=830,
    username="admin",
    password="admin",
    hostkey_verify=False,
    device_params={"name": "iosxe"}
)

filter_intf = """
<interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces"/>
"""
reply = device.get_config(source="running", filter=("subtree", filter_intf))
print(reply.xml)

ns = {"if": "urn:ietf:params:xml:ns:yang:ietf-interfaces"}
root = ET.fromstring(reply.xml)

for intf in root.findall(".//if:interface", ns):
    name = intf.find("if:name", ns).text
    desc = intf.find("if:description", ns)
    print(name, desc.text if desc is not None else "(no description)")

print("-----------------------------------------------------------------")
config = """
<config>
	<interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
		<interface>
			<name>Loopback1</name>
			<description>Test</description>
			<type xmlns:ianaift="urn:ietf:params:xml:ns:yang:iana-if-type">ianaift:softwareLoopback</type>
			<enabled>true</enabled>
		</interface>
	</interfaces>
</config>
"""
device.edit_config(target="running", config=config)
print("Loopback1 created")
device.close_session()