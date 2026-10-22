# file: lab10_jinja_adv.py
import requests
from jinja2 import Template, FileSystemLoader, Environment
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import urllib3
import os
from lab9_exec_control import wait_for_task, get_device_list, get_token

# Load environment variables
load_dotenv()
BASE_URL = os.environ["CATC_BASE_URL"]
USERNAME = os.environ["CATC_USERNAME"]
PASSWORD = os.environ["CATC_PASSWORD"]

# ignore certificate warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load Jinja Template 
env = Environment(loader=FileSystemLoader("./template"), trim_blocks=True, lstrip_blocks=True)

def get_template_project(headers):
    """Get template project from catc"""
    template_url=f"{BASE_URL}/dna/intent/api/v1/template-programmer/project"
    print("Getting templates")
    resp = requests.get(template_url, headers=headers, verify=False)
    resp.raise_for_status()
    return resp

def create_project(headers, payload):
    """Create new project template"""
    template_url = f"{BASE_URL}/dna/intent/api/v1/template-programmer/project"
    resp = requests.post(template_url, headers=headers, json=payload, verify=False)
    resp.raise_for_status()
    return resp

def create_template(headers, project_id, payload):
    """Create new template after rendering from jinja"""
    create_template_url = f"{BASE_URL}/dna/intent/api/v1/template-programmer/project/{project_id}/template"
    resp = requests.post(create_template_url, headers=headers, json=payload, verify=False)

# Error verification step
    print("Status:", resp.status_code)
    print("Error:", resp.text)

    resp.raise_for_status()
    return resp

def get_template_by_id(headers, template_id):
    """Get template details by ID"""
    url = f"{BASE_URL}/dna/intent/api/v1/template-programmer/template/{template_id}"
    resp = requests.get(url, headers=headers, verify=False)
    resp.raise_for_status()
    return resp

def preview_template(headers, payload):
    url = f"{BASE_URL}/dna/intent/api/v1/template-programmer/template/preview"
    resp = requests.put(url, headers=headers, json=payload, verify=False)
    resp.raise_for_status()
    return resp

def version_template(headers, payload):
    url = f"{BASE_URL}/dna/intent/api/v1/template-programmer/template/version"
    resp = requests.post(url, headers=headers, json=payload, verify=False)
    resp.raise_for_status()
    return resp

def get_template_versions(headers, template_id):
    """Get committed template versions"""
    url = f"{BASE_URL}/dna/intent/api/v1/template-programmer/template/version/{template_id}"
    resp = requests.get(url, headers=headers, verify=False)
    resp.raise_for_status()
    return resp

def deploy_template(headers, payload):
    """Deploy a committed template to a device"""
    url = f"{BASE_URL}/dna/intent/api/v1/template-programmer/template/deploy"
    resp = requests.post(url, headers=headers, json=payload, verify=False)
    print("Deployment status:", resp.status_code)
    print("Deployment response:", resp.text)
    resp.raise_for_status()
    return resp

# Before actual deployment, prepare payload and basic checks
def prepare_deploy_payload(versions, preview, template_id, sw1, device):
    """Validate preview and prepare deployment payload"""

    # Find committed template version
    versioned_template_id = None

    for template_record in versions.json():
        for version in template_record["versionsInfo"]:
            if version.get("version") == "1":
                versioned_template_id = version["id"]
                break

    if versioned_template_id is None:
        raise RuntimeError("Committed template version not found")

    # Validate configuration preview
    expected_cli = "interface Vlan1\n description ENAUTO-LAB-TEST"
    actual_cli = preview.json()["cliPreview"].strip()

    if actual_cli != expected_cli:
        raise RuntimeError("Unexpected configuration preview")

    if preview.json()["validationErrors"]:
        raise RuntimeError("Template preview contains validation errors")

    # Prepare deployment payload
    deploy_payload = {
        "forcePushTemplate": False,
        "isComposite": False,
        "templateId": template_id,
        "targetInfo": [
            {
                "id": sw1["id"],
                "type": "MANAGED_DEVICE_UUID",
                "versionedTemplateId": versioned_template_id,
                "params": {"device": device}
            }
        ]
    }
    return deploy_payload

def get_deployment_status(headers, deployment_id):
    """Get Catalyst Center template deployment status"""
    url = f"{BASE_URL}/dna/intent/api/v1/template-programmer/template/deploy/status/{deployment_id}"
    resp = requests.get(url, headers=headers, verify=False)
    resp.raise_for_status()
    return resp

if __name__ == "__main__":
# Define data
    interfaces = [
        {
            "name": "Vlan1",
            "desc": "ENAUTO-LAB-TEST",
            "managed": True
        }
    ]

    device = {
        "hostname": "sw1",
        "interfaces": interfaces
    }

    template = env.get_template("interface.j2")
    output = template.render(device=device)
    print("*"*40)
    #print(output)
    print("*"*40)

# Get token is imported from lab9 and used here
    token = get_token()
    new_headers = {"X-Auth-Token": token, "Content-Type": "application/json"}

# Determine deviceTypes
    devices = get_device_list(new_headers)
    for dev in devices["response"]:
        if dev["hostname"] == "sw1":
            print({
                "family": dev.get("family"),
                "series": dev.get("series"),
                "type": dev.get("type"),
                "softwareType": dev.get("softwareType")
            })

    cat_template = get_template_project(new_headers)
    print("*"*40)
    payload = {
        "name": "ENAUTO-Lab09-10",
        "description": "ENAUTO interface description template lab"
    }
    if any(p["name"] == payload["name"] for p in cat_template.json()):
        print("Project already exists. Skipping creation.")
    else:
        project_id = create_project(new_headers, payload)
        task_id = project_id.json()["response"]["taskId"]

# wait for task is imported from lab9 and used here
        task_result = wait_for_task(task_id, new_headers)
        print("Task completed:", task_result.get("isError") is False)

    cat_template = get_template_project(new_headers)
    for p in cat_template.json():
        if p["name"] == payload["name"]:
            project = p
            break

    print("Project ID:", project["id"])

# create template
    sw1 = None
    for d in devices["response"]:
        if d["hostname"] == "sw1":
            sw1 = d
            break
    if sw1 is None:
        raise RuntimeError("Device sw1 not found in inventory")
    
    with open("./template/interface.j2") as f:
        template_content = f.read()
    template_payload = {
        "name": "ENAUTO-Interface-Descriptions",
        "projectName": payload["name"],
        "language": "JINJA",
        "softwareType": sw1["softwareType"],
        "deviceTypes": [{
            "productFamily": sw1["family"],
            "productSeries": sw1["series"],
            "productType": sw1["type"]
        }],
        "templateContent": template_content
    }

# Get template id
    for t in project["templates"]:
        if t["name"] == template_payload["name"]:
            template_id = t["id"]
            break

# Verify template stored in Catalyst Center
    result = get_template_by_id(new_headers, template_id)
    print("Language:", result.json().get("language"))
    # print("Template content:", result.json().get("templateContent"))
    print("*"*40)
    preview_payload = {
        "templateId": template_id,
        "params": {"device": device}
    }
# Preview template
    preview = preview_template(new_headers, preview_payload)
    print("Controller preview:")
    print(preview.json()["cliPreview"])
    print("Validation errors:", preview.json()["validationErrors"])
# Check template versions
    print("*"*40)
    versions = get_template_versions(new_headers, template_id)
    print("Template versions:")
    print(versions.json())

# Checks and start deployment
    deploy_payload = prepare_deploy_payload(versions, preview, template_id, sw1, device)
    deployment_id = "81a2fce1-2081-47c0-b9cc-1fa04716ad2a"
    deployment_status = get_deployment_status(new_headers, deployment_id)
    print("*"*40)
    print("Deployment status:")
    print(deployment_status.json())