import asyncio
from fastmcp import Client
from server import mcp


async def main():
    async with Client(mcp) as c:
        print("TOOLS:", [t.name for t in await c.list_tools()])
        print("RESOURCES:", [str(r.uri) for r in await c.list_resources()])
        print(await c.call_tool("get_interface_status"))
        print(await c.read_resource("device://iosxe-01/interfaces"))


asyncio.run(main())
