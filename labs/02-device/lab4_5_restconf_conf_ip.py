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

payload_1 = {
    "ietf-interfaces:interfaces": {
        "interface": [
            {
                "name": "GigabitEthernet2",
                "description": "Configured by RESTCONF",
                "enabled": True,
                "ietf-ip:ipv4": {
                    "address": [
                        {
                            "ip": "10.0.12.1",
                            "netmask": "255.255.255.252"
                        }
                    ]
                }
            },
            {
                    "name": "GigabitEthernet3",
                    "description": "Configured by RESTCONF",
                    "enabled": True,
                    "ietf-ip:ipv4": {
                        "address": [
                        {
                            "ip": "192.168.1.1",
                            "netmask": "255.255.255.0"
                        }
                    ]
                }
            },
            {
                "name": "Loopback0",
                "description": "Configured by RESTCONF",
                "enabled": True,
                "type": "iana-if-type:softwareLoopback",
                "ietf-ip:ipv4": {
                    "address": [
                        {
                            "ip": "10.255.1.1",
                            "netmask": "255.255.255.255"
                        }
                    ]
                }
            }
        ]     
    }
}

patch_1 = session.patch(
    f"https://{devices[0]}/restconf/data/ietf-interfaces:interfaces",
    json=payload_1
    )

print("\n=== PATCH RESULT ===")
print(f"Status Code: {patch_1.status_code}")
print(f"Response Body: {patch_1.text}")

payload_2 = {
    "ietf-interfaces:interfaces": {
        "interface": [
            {
                "name": "GigabitEthernet2",
                "description": "Configured by RESTCONF",
                "enabled": True,
                "ietf-ip:ipv4": {
                    "address": [
                        {
                            "ip": "10.0.12.2",
                            "netmask": "255.255.255.252"
                        }
                    ]
                }
            },
            {
                "name": "GigabitEthernet3",
                "description": "Configured by RESTCONF",
                "enabled": True,
                "ietf-ip:ipv4": {
                    "address": [
                        {
                            "ip": "10.0.23.1",
                            "netmask": "255.255.255.252"
                        }
                    ]
                }
            },
            {
                "name": "Loopback0",
                "description": "Configured by RESTCONF",
                "enabled": True,
                "type": "iana-if-type:softwareLoopback",
                "ietf-ip:ipv4": {
                    "address": [
                        {
                            "ip": "10.255.2.2",
                            "netmask": "255.255.255.255"
                        }
                    ]
                }
            }
        ]
    }
}

patch_2 = session.patch(
    f"https://{devices[1]}/restconf/data/ietf-interfaces:interfaces",
    json=payload_2
    )

print("\n=== PATCH RESULT ===")
print(f"Status Code: {patch_2.status_code}")
print(f"Response Body: {patch_2.text}")

payload_3 = {
    "ietf-interfaces:interfaces": {
        "interface": [
            {
                "name": "GigabitEthernet2",
                "description": "Configured by RESTCONF",
                "enabled": True,
                "ietf-ip:ipv4": {
                    "address": [
                        {
                            "ip": "10.0.23.2",
                            "netmask": "255.255.255.252"
                        }
                    ]
                }
            },
            {
                "name": "GigabitEthernet3",
                "description": "Configured by RESTCONF",
                "enabled": True,
                "ietf-ip:ipv4": {
                    "address": [
                        {
                            "ip": "192.168.2.1",
                            "netmask": "255.255.255.0"
                        }
                    ]
                }
            },
            {
                "name": "Loopback0",
                "description": "Configured by RESTCONF",
                "enabled": True,
                "type": "iana-if-type:softwareLoopback",
                "ietf-ip:ipv4": {
                    "address": [
                        {
                            "ip": "10.255.3.3",
                            "netmask": "255.255.255.255"
                        }
                    ]
                }
            }
        ]
    }
}

patch_3 = session.patch(
    f"https://{devices[2]}/restconf/data/ietf-interfaces:interfaces",
    json=payload_3
    )

print("\n=== PATCH RESULT ===")
print(f"Status Code: {patch_3.status_code}")
print(f"Response Body: {patch_3.text}")

for device in devices:
    base_url = f"https://{device}/restconf/data/"
    conn = session.get(url=base_url + "ietf-interfaces:interfaces")

    print(f"\n=== {device} ===")
    print(f"Status Code: {conn.status_code}")

    interfaces = conn.json()["ietf-interfaces:interfaces"]["interface"]

    for interface in interfaces:
        name = interface["name"]
        description = interface.get("description", "<no description>")

        ipv4 = interface.get("ietf-ip:ipv4", {})
        addresses = ipv4.get("address", [])

        if addresses:
            ip_text = ", ".join(
                f'{addr["ip"]} {addr.get("netmask", "")}'
                for addr in addresses
            )
        else:
            ip_text = "<no IPv4>"

        print(f"{name} | {description} | {ip_text}")