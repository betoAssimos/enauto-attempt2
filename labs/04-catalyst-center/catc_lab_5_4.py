import os
from dotenv import load_dotenv
import urllib3
from dnacentersdk import DNACenterAPI

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()

BASE_URL = os.environ["CATC_BASE_URL"]
USERNAME = os.environ["CATC_USERNAME"]
PASSWORD = os.environ["CATC_PASSWORD"]

def build_client():
    """Build a DNACenterAPI client."""
    api = DNACenterAPI(username=USERNAME, password=PASSWORD, base_url=BASE_URL, verify=False)
    return api

if __name__ == "__main__":
    api = build_client()
    r = api.devices.get_device_list()
    print([d["hostname"] for d in r["response"]])
    print(type(r))
    r = api.devices.get_device_list(offset=2, limit=2)
    print([n for n in dir(api.devices) if "paginat" in n.lower()])
    print([d["hostname"] for d in r["response"]])
    r = api.devices.get_device_list(offset=1, limit=1000)
    print([d["hostname"] for d in r["response"]])

try:
    r = api.devices.get_device_list(offset=0, limit=2)
    print("accepted:", [d["hostname"] for d in r["response"]])
except Exception as e:
    print(type(e).__name__, e)