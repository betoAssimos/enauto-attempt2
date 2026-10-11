from ncclient import manager
from pathlib import Path

device = manager.connect(
    host="172.30.30.11",
    port=830,
    username="admin",
    password="admin",
    hostkey_verify=False,
    device_params={"name": "iosxe"},
)

models = [
    ("ietf-interfaces", "2014-05-08"),
    ("ietf-ip", "2014-06-16"),
]

output_dir = Path(__file__).resolve().parent / "yang-models"
output_dir.mkdir(exist_ok=True)

for model, revision in models:
    reply = device.get_schema(
        model,
        version=revision,
    )

    path = output_dir / f"{model}.yang"
    path.write_text(reply.data, encoding="utf-8")

    print(f"Saved: {path}")

device.close_session()