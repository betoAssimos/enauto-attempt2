import json
from pathlib import Path
from fastmcp import FastMCP
from collector import get_interfaces
from fastmcp.exceptions import ToolError

inv_file = Path(__file__).parent / "inventory.json"

mcp = FastMCP(name="Enauto-2")

@mcp.tool
def get_device_inventory() -> list[dict]:
    """Return the name, host and device_type of inventory."""
    with inv_file.open() as f:
        return json.load(f)

@mcp.tool
def get_interface_status(device: str) -> list[dict]:
    """Return the interface table of one device. Pass a device name from get_device_inventory."""
    with inv_file.open() as f:
        inventory = json.load(f)
    for entry in inventory:
        if entry["name"] == device:
            return get_interfaces(entry)
    raise ToolError(f"Unknown device: {device}")    

if __name__ == "__main__":
    mcp.run(transport="stdio")