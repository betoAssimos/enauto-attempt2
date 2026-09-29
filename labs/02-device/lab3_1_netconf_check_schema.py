from ncclient import manager
import os
from dotenv import load_dotenv

load_dotenv()

user = os.getenv("IOS_DEVICE_USER")
pwd = os.getenv("IOS_DEVICE_PASS")

modules = [
    "Cisco-IOS-XE-ospf",
    "cisco-semver",
    "Cisco-IOS-XE-types",
    "Cisco-IOS-XE-native",
    "Cisco-IOS-XE-features",
    "Cisco-IOS-XE-isis",
    "Cisco-IOS-XE-snmp",
    "Cisco-IOS-XE-segment-routing",
    "Cisco-IOS-XE-ospf-obsolete",
]

with manager.connect(
    host="172.30.30.11",
    port=830,
    username=user,
    password=pwd,
    hostkey_verify=False,
    device_params={"name": "iosxe"}
) as m:

    for module in modules:
        print(f"Downloading {module}...")

        schema = m.get_schema(module)

        with open(f"{module}.yang", "w") as f:
            f.write(schema.data)