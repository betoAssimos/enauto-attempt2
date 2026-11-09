from catalystcentersdk import CatalystCenterAPI
from dotenv import load_dotenv
import urllib3
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

# Environment variables
base_url = os.getenv("CATC_BASE_URL")
username = os.getenv("CATC_USERNAME")
password = os.getenv("CATC_PASSWORD")

# Initialize Catalyst Center SDK
api = CatalystCenterAPI(
    username=username,
    password=password,
    base_url=base_url,
    version="2.3.7.9",
    verify=False
)

# Retrieve device inventory
result = api.devices.get_device_list()

# Display devices
for device in result.response:
    print(f"Hostname: {device.hostname}")
    print(f"Management IP: {device.managementIpAddress}")
    print("---------------------------")