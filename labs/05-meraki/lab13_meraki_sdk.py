import os
import meraki
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.environ["MERAKI_HOST"]
API_KEY = os.environ["MERAKI_API_KEY"]


def get_devices(dashboard, org_id):
    devices = dashboard.organizations.getOrganizationDevices(
        org_id,
        perPage=3,
        total_pages="all"
    )
    return devices


def show_unnamed_devices(devices, network_id):
    for device in devices:
        if device["networkId"] == network_id and device["name"] == "":
            print(f"{device['serial']} | {device['model']} | {device['productType']}")


if __name__ == "__main__":
    dashboard = meraki.DashboardAPI(
        api_key=API_KEY,
        base_url=BASE_URL,
        wait_on_rate_limit=True,
        suppress_logging=True
    )

    org_id = "669910444571370741"
    network_id = "L_669910444571385196"

    devices = get_devices(dashboard, org_id)

    print(f"Total devices: {len(devices)}")
    print("*" * 40)
    show_unnamed_devices(devices, network_id)