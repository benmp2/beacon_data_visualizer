import asyncio
from bleak import BleakScanner

async def run():
    devices = await BleakScanner.discover()
    device_list = []
    for d in devices:
        device_list.append((d.address, d.rssi))
    
    device_list =  sorted(device_list, key=lambda tup: tup[1],reverse=True)
    for el in device_list:
        print(f'{el[0]} - rssi: {el[1]}')

loop = asyncio.get_event_loop()
loop.run_until_complete(run())