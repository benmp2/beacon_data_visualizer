import asyncio
from bleak import discover

beacon_MAC = "C5:00:36:52:DC:DF"

async def run():
    devices = await discover()
    for d in devices:
        if d.address == beacon_MAC:
            print(d.address, d.name, d.metadata, d.rssi)            
            print(dir(d))
            
loop = asyncio.get_event_loop()
loop.run_until_complete(run())