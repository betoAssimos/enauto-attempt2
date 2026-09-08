from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException, ReadTimeout

device_1 = {
    # wrong username
    "device_type": "cisco_ios",
    "host": "172.30.30.11",
    "username": "administer",
    "password": "admin",
}

device_2 = {
    # wrong device_type
    "device_type": "arista_eos",
    "host": "172.30.30.12",
    "username": "admin",
    "password": "admin",
}

device_3 = {
    "device_type": "cisco_ios",
    "host": "172.30.30.13",
    "username": "admin",
    "password": "admin",
}

# Group devices together for loop
inventory = [device_1, device_2, device_3]

commands = [
    # interfaces instead of interface
    "interfaces GigabitEthernet1",
    "description Container Management Interface",
]

result_report = {
    "success": [],
    "failed": []
}

for device in inventory:
    host = device["host"]
    print(f"Connecting to {host}...")

    try:
        with ConnectHandler(**device) as conn:
            hostname = (conn.send_command("show run | include ^hostname")).split(maxsplit=1)[1]
            conn.send_config_set(commands)
            verification = conn.send_command("show interfaces GigabitEthernet1 description")
            result_report["success"].append({
                "host": host,
                "hostname": hostname,
                "status": "Configured and verified successfully",
                "details": verification.strip()
            })
            print(f"[{host}] Success!")
    except NetmikoAuthenticationException:
        error_msg = f"[{host}] Authentication failed. Please check your credentials."
        print(f"[{host}] FAILED: {error_msg}")
        result_report["failed"].append({"host": host, "error": error_msg})

    except NetmikoTimeoutException:
        error_msg = "Connection timeout: Device is unreachable or not responding."
        print(f"[{host}] FAILED: {error_msg}")
        result_report["failed"].append({"host": host, "error": error_msg})

    except ReadTimeout as error:
        error_msg = "Session preparation timeout, check device_type"
        print(f"[{host}] FAILED: {error_msg}")
        result_report["failed"].append({"host": host, "error": error_msg})

print("\n" + "="*40)
print("          FINAL EXECUTION REPORT          ")
print("="*40)
print(f"Successful Devices ({len(result_report['success'])}):")
for item in result_report["success"]:
    print(f"  - {item['host']} ({item['hostname']}) - {item['status']}")
    print(f"    Verification Output: {item['details']}")

print(f"\nFailed Devices ({len(result_report['failed'])}):")
for item in result_report["failed"]:
    print(f"  - {item['host']}: {item['error']}")
print("="*40)