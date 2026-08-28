import os
from dotenv import load_dotenv
from netmiko import ConnectHandler

load_dotenv(override=True)

DEVICE = {
    "device_type": os.environ["IOS_DEVICE_TYPE"],
    "host": os.environ["IOS_DEVICE_HOST"],
    "username": os.environ["IOS_DEVICE_USER"],
    "password": os.environ["IOS_DEVICE_PASS"],
    "fast_cli": False,
}


def get_interfaces():
    with ConnectHandler(**DEVICE) as conn:
        return conn.send_command("show ip interface brief", use_textfsm=True)


if __name__ == "__main__":
    print(get_interfaces())
