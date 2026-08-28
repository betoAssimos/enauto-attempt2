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
    version = ""
    print(version)
    api = DNACenterAPI(username=USERNAME, password=PASSWORD, base_url=BASE_URL, verify=False, version=version)
    return api

if __name__ == "__main__":
    api = build_client()
    #print("Client token:", api.access_token)
    #print("Token count:", len(api.access_token))
    #print(dir(api))
    #print("Site health summary:", api.sites.get_site_health())
    r = api.sites.get_site_health()
    print(type(r))
    print(r["response"][0]["siteName"])
    print(r.response[0].siteName)