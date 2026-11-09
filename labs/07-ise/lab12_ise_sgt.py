import os
import requests
import urllib3
import json
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from ciscoisesdk import IdentityServicesEngineAPI

# Initialize environment and remove certificate warning
load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables
BASE_URL = os.environ["ISE_HOST"]
USERNAME = os.environ["ISE_USERNAME"]
PASSWORD = os.environ["ISE_PASSWORD"]

def get_sgt(session):
    req = session.get(url=BASE_URL+"/ers/config/sgt", headers={"X-CSRF-Token": "fetch"})
    return req

def create_sgt(session, csrf_token, payload):
    headers = {"Content-Type": "application/json", "X-CSRF-Token": csrf_token}
    url = f"{BASE_URL}/ers/config/sgt"
    req = session.post(url, headers=headers, json=payload)
    return req


# Start
if __name__ == "__main__":
    # Define session variables to maintain one session through the script
    session = requests.Session()
    headers = {"Accept" : "application/json"}
    session.auth = HTTPBasicAuth(USERNAME,PASSWORD)
    session.headers.update(headers)
    session.verify = False
    # Get SGT
    sgt = get_sgt(session)
    data = sgt.json()
    resources = data["SearchResult"]["resources"]
    # Check resource name and id, commented after use
    for resource in  resources:
        print(resource["name"], resource["id"])
    csrf_token = sgt.headers.get("X-CSRF-Token")
    if csrf_token:
        print("CSRF token received")
    else:
        print("CSRF token not returned by ISE")
        raise SystemExit(1)

    # Creating payload for POST request
    payload = {
        "Sgt": {
            "name": "ENAUTO_LAB12",
            "description": "Temporary security group for ENAUTO lab 12",
            "value": 5001
        }
    }

    new_sgt = create_sgt(session, csrf_token, payload)
    print(f"POST Status Code: {new_sgt.status_code}")
    if new_sgt.status_code == 201:
        print("SGT created successfully")
        print(f"Location: {new_sgt.headers.get('Location')}")
    else:
        print(f"POST failed: {new_sgt.status_code}")
        print(new_sgt.text)

    # Test using SDK
    api = IdentityServicesEngineAPI(
        username=USERNAME,
        password=PASSWORD,
        base_url=BASE_URL,
        uses_api_gateway=True,
        uses_csrf_token=True,
        verify=False
    )

    sgt_id = "052d9600-f5c5-46b1-aabc-a155a4b4b554"

    result = api.security_groups.get_by_id(id=sgt_id)
    sgt = result.response.Sgt

    print("*"*40)
    print(sgt.name, sgt.value, sgt.id)