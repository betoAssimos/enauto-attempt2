from ncclient import manager
from pathlib import Path

device = manager.connect(
    host="172.30.30.11",
    port=830,
    username="admin",
    password="admin",
    hostkey_verify=False,
    device_params={"name": "iosxe"}
)

for cap in device.server_capabilities:
    print(cap)

reply = device.get_schema("ietf-interfaces")

Path.home().joinpath("yang-models-lab", "ietf-interfaces.yang").write_text(
    reply.data,
    encoding="utf-8"
)

device.close_session()
