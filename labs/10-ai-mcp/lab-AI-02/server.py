from fastmcp import FastMCP
from collector import get_interfaces

mcp = FastMCP(name="enauto-device")


@mcp.tool
def get_interface_status():
    """Return the interface table from the lab IOS-XE device."""
    return get_interfaces()


@mcp.resource("device://iosxe-01/interfaces")
def interfaces_resource():
    """Current interface table for the lab IOS-XE device."""
    return get_interfaces()


if __name__ == "__main__":
    mcp.run(transport="stdio")
