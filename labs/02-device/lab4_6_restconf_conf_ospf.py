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


payload_ospf = {
    "Cisco-IOS-XE-native:native": {
        "router": {
            "Cisco-IOS-XE-ospf:router-ospf": {
                "ospf": {
                    "process-id": [
                        {
                            "id": 1,
                            "router-id": "1.1.1.1",
                            "network": [
                                {
                                    "ip": "10.0.12.0",
                                    "wildcard": "0.0.0.3",
                                    "area": 1
                                },
                                {
                                    "ip": "192.168.1.0",
                                    "wildcard": "0.0.0.255",
                                    "area": 1
                                },
                                {
                                    "ip": "10.255.1.1",
                                    "wildcard": "0.0.0.0",
                                    "area": 1
                                }
                            ]
                        }
                    ]
                }
            }
        }
    }
}

payload_ospf_2 = {
    "Cisco-IOS-XE-native:native": {
        "router": {
            "Cisco-IOS-XE-ospf:router-ospf": {
                "ospf": {
                    "process-id": [
                        {
                            "id": 1,
                            "router-id": "2.2.2.2",
                            "network": [
                                {
                                    "ip": "10.0.12.0",
                                    "wildcard": "0.0.0.3",
                                    "area": 1
                                },
                                {
                                    "ip": "10.0.23.0",
                                    "wildcard": "0.0.0.3",
                                    "area": 2
                                },
                                {
                                    "ip": "10.255.2.2",
                                    "wildcard": "0.0.0.0",
                                    "area": 0
                                }
                            ]
                        }
                    ]
                }
            }
        }
    }
}

payload_ospf_3 = {
    "Cisco-IOS-XE-native:native": {
        "router": {
            "Cisco-IOS-XE-ospf:router-ospf": {
                "ospf": {
                    "process-id": [
                        {
                            "id": 1,
                            "router-id": "3.3.3.3",
                            "network": [
                                {
                                    "ip": "10.0.23.0",
                                    "wildcard": "0.0.0.3",
                                    "area": 2
                                },
                                {
                                    "ip": "192.168.2.0",
                                    "wildcard": "0.0.0.255",
                                    "area": 2
                                },
                                {
                                    "ip": "10.255.3.3",
                                    "wildcard": "0.0.0.0",
                                    "area": 2
                                }
                            ]
                        }
                    ]
                }
            }
        }
    }
}
payloads = [
    payload_ospf,
    payload_ospf_2,
    payload_ospf_3
]

for device, payload in zip(devices, payloads):
    patch_ospf = session.patch(
        f"https://{device}/restconf/data/Cisco-IOS-XE-native:native",
        json=payload
    )

    print(f"\n=== PATCH {device} ===")
    print(f"Status Code: {patch_ospf.status_code}")

for device in devices:
    url = (
        f"https://{device}/restconf/data/"
        "Cisco-IOS-XE-native:native/"
        "router/"
        "Cisco-IOS-XE-ospf:router-ospf/"
        "ospf/"
        "process-id"
    )

    conn = session.get(url=url)

    print(f"\n=== {device} OSPF ===")
    print(f"Status Code: {conn.status_code}")

    if conn.status_code == 200:
        data = conn.json()

        ospf_processes = data.get("Cisco-IOS-XE-ospf:process-id", [])

        for ospf in ospf_processes:
            print(f"Process ID: {ospf.get('id')}")
            print(f"Router ID: {ospf.get('router-id', '<not configured>')}")

            for network in ospf.get("network", []):
                print(
                    f"Network: {network.get('ip')} "
                    f"Wildcard: {network.get('wildcard')} "
                    f"Area: {network.get('area')}"
                )

    else:
        print(conn.text)