import os
from dotenv import load_dotenv
import urllib3
import inspect
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
    print([m for m in dir(api.devices) if not m.startswith("_")])
    #r = api.sites.get_site_health()
    #print(type(r))
    #print(r["response"][0]["siteName"])
    #print(r.response[0].siteName)