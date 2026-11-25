import asyncio
from fastmcp import Client
from server import mcp


async def main():
    async with Client(mcp) as client:
        tools = await client.list_tools()
        print("TOOLS:", [t.name for t in tools])
        print("INPUT SCHEMA:", tools[0].inputSchema)
        print("OUTPUT SCHEMA:", tools[0].outputSchema)

        result = await client.call_tool("get_device_inventory")
        print("STRUCTURED:", result.structured_content)
        print("DATA:", result.data)

        print("INPUT SCHEMA 2:", tools[1].inputSchema)

        result = await client.call_tool("get_interface_status", {"device": "xe"})
        print("XE:", result.data)

        for bad in [{"device": ""}, {"device": 123}, {}]:          # the three inputs from the table
            try:
                await client.call_tool("get_interface_status", bad)
            except Exception as e:
                print("REJECTED", bad, "->", e)


asyncio.run(main())