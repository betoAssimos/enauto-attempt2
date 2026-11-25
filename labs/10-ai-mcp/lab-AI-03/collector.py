import os
from dotenv import load_dotenv
from netmiko import ConnectHandler

load_dotenv(override=True)

def get_interfaces(device: dict) -> list[dict]:
    DEVICE = {
        "device_type": device["device_type"],
        "host": device["host"],
        "username": os.environ["IOS_DEVICE_USER"],
        "password": os.environ["IOS_DEVICE_PASS"],
    }
    with ConnectHandler(**DEVICE) as conn:
        return conn.send_command("show ip interface brief", use_textfsm=True)


if __name__ == "__main__":
    test_device = {"name": "xe", "host": "172.20.20.19", "device_type": "cisco_xe"}
    print(get_interfaces(test_device))