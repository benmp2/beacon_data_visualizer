"""
Detection callback w/ scanner
--------------
Example showing what is returned using the callback upon detection functionality
Updated on 2020-10-11 by bernstern <bernie@allthenticate.net>
"""

import asyncio
from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
import logging
import datetime as dt

# from System import Guid
# from bleak.Devices.Bluetooth.Advertisement import BluetoothLEAdvertisementFilter, BluetoothLEAdvertisement

logging.basicConfig()

# BEACON_MAC = 'C5:00:36:52:DC:DF'
BEACON_MAC = 'E0:F0:23:8C:7B:F7'

ADVERTISEMENT_SERVICE_DATA_UUID = '0000fe9a-0000-1000-8000-00805f9b34fb'

def twos_comp(val, bits):
    """compute the 2's complement of int value val"""
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val                         # return positive value as is

def calc_g_units(acceleration):

    acceleration = twos_comp(acceleration, 8)
    acceleration = int(acceleration) * 2 / 127.0
    acceleration = round(acceleration,2)

    return acceleration

def accelerometer_callback(device: BLEDevice, advertisement_data: AdvertisementData):
    if device.address == BEACON_MAC:
        # print(device.address, "RSSI:", device.rssi, advertisement_data)

        service_data = advertisement_data.service_data[ADVERTISEMENT_SERVICE_DATA_UUID]
        # not_this= b'"\xbe\xd9\xccx;\x86\xde\x93\x01\xff\xff\xff\xff\x90 _\xf0%\x17'
        # not_that= b'"\xbe\xd9\xccx;\x86\xde\x93\x01\xff\xff\xff\xff\x90 `\xf0%\x17'

        subframe_type = (service_data[9] & 0b00000011)
        if 0 == subframe_type:
            print(device.address,
                dt.datetime.now().time(),
                f'subframe A==0, B==1:{subframe_type}',)
            # print(
            #     f'\tx:{calc_g_units(service_data[10])}\n',
            #     f'\ty:{calc_g_units(service_data[11])}\n',
            #     f'\tz:{calc_g_units(service_data[12])}\n')
                # f'isMoving {(service_data[15] & 0b00000011) == 1}')


async def run():
    # https://github.com/hbldh/bleak/issues/230#issuecomment-652822031
    # scanner = BleakScanner(AdvertisementFilter=)
    scanner = BleakScanner()
    scanner.register_detection_callback(accelerometer_callback)
    while True:
        await scanner.start()
        await asyncio.sleep(5)
        await scanner.stop()

loop = asyncio.get_event_loop()
loop.run_until_complete(run())