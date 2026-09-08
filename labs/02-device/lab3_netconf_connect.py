from ncclient import manager
from ncclient.operations import RPCError
import xml.dom.minidom

hosts = ["172.30.30.11", "172.30.30.12", "172.30.30.13"]
for host in hosts:
    print("="*40)
    print(f"Connecting to {host}...")
    device = {
        "host": host,
        "port": 830,
        "username": "admin",
        "password": "admin",
        "hostkey_verify": False,
        "device_params": {"name": "iosxe"}
    }

# CAPABILITIES CHECK
    with manager.connect(**device) as conn:
        print("=== CANDIDATE CAPABILITIES CHECK ===")
        supports_candidate = False
        for capability in conn.server_capabilities:
            if "ietf-interfaces" in capability:
                print(f"ietf-interfaces supported: {capability}")
            if ":candidate" in capability:
                supports_candidate = True
        print(f"Candidate datastore supported: {supports_candidate}")
        
        print("=== DEVICE CAPABILITIES ===")
        for capability in conn.server_capabilities:
            if "ietf-interfaces" in capability:
                #print(capability)
                print("="*40)

            
        interface_filter = """
        <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces"/>
        """
        #print("\nRetrieving interface operational state...")
        netconf_reply = conn.get(filter=("subtree", interface_filter))
        dom = xml.dom.minidom.parseString(netconf_reply.xml)
        #print(dom.toprettyxml(indent="  "))
        print("="*40)

        description_filter = """
        <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
            <interface>
                <name>GigabitEthernet1</name>
                <description/>
            </interface>
        </interfaces>
        """
        # get config data with filter
        print("\nRetrieving interface description...")
        netconf_reply = conn.get_config(source="running", filter=("subtree", description_filter))
        dom = xml.dom.minidom.parseString(netconf_reply.xml)
        print(dom.toprettyxml(indent="  "))
        print("="*40)

        # edit config data - descriptions
        print("\nUpdating interface description...")
        new_description = """
            <config>
                <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
                    <interface>
                        <name>GigabitEthernet1</name>
                        <description>Container Management Interface</description>
                    </interface>
                </interfaces>
            </config>
        """
        conn.edit_config(target="running", config=new_description)
        # get config data with filter
        print("\nRetrieving interface description...")
        netconf_reply = conn.get_config(source="running", filter=("subtree", description_filter))
        dom = xml.dom.minidom.parseString(netconf_reply.xml)
        print(dom.toprettyxml(indent="  "))
        print("="*40)
            
