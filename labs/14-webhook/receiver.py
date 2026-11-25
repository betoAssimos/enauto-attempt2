import os
import requests
import urllib3
from dotenv import load_dotenv
from flask import Flask, request
from requests.auth import HTTPBasicAuth

load_dotenv(override=True)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = os.environ["CATC_BASE_URL"]
USERNAME = os.environ["CATC_USERNAME"]
PASSWORD = os.environ["CATC_PASSWORD"]

session = requests.Session()
session.verify = False
session.headers.update({"Accept": "application/json"})

app = Flask(__name__)

#################### FUNCTIONS #########################
def get_token(session):
    """Get a token from the Catalyst Center API."""
    url = f"{BASE_URL}/dna/system/api/v1/auth/token"
    r = session.post(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), timeout=30)
    r.raise_for_status()
    return r.json()["Token"]

def get_device(session, device_id):
    url = f"{BASE_URL}/dna/intent/api/v1/network-device/{device_id}"
    resp = session.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()["response"]

@app.post("/webhook")
def receive_event():
    payload = request.get_json()
    event_type = payload.get("eventId")
    device_id = payload.get("network", {}).get("deviceId")
    print(f"event received: {event_type}")

    if device_id:
        session.headers.update({"X-Auth-Token": get_token(session)})
        device = get_device(session, device_id)
        print(device)

    return {"status": "received"}, 200