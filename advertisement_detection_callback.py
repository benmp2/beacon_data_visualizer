"""
Detection callback w/ scanner
--------------
Example showing what is returned using the callback upon detection functionality
Updated on 2020-10-11 by bernstern <bernie@allthenticate.net>
"""
import math
import asyncio
from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
import logging
import datetime as dt

import estimote_parser.parser as ep

logging.basicConfig()

# Each beacon has a unique MAC Address:
# BEACON_MAC = 'C5:00:36:52:DC:DF' 
BEACON_MAC = 'E0:F0:23:8C:7B:F7'

#UUID doesnt change:
ADVERTISEMENT_SERVICE_DATA_UUID = '0000fe9a-0000-1000-8000-00805f9b34fb'

def accelerometer_callback(device: BLEDevice, advertisement_data: AdvertisementData):
    if device.address == BEACON_MAC:
        # print(device.address, "RSSI:", device.rssi, advertisement_data)

        service_data = advertisement_data.service_data[ADVERTISEMENT_SERVICE_DATA_UUID]
        # not_this= b'"\xbe\xd9\xccx;\x86\xde\x93\x01\xff\xff\xff\xff\x90 _\xf0%\x17'
        # not_that= b'"\xbe\xd9\xccx;\x86\xde\x93\x01\xff\xff\xff\xff\x90 `\xf0%\x17'

        protocolVersion = (service_data[0] & 0b11110000) >> 4

        subframe_type = (service_data[9] & 0b00000011)
        subframe_type = 'A' if subframe_type == 0 else 'B'
        now = dt.datetime.now().time()
        print(
            device.address, 
            now, 
            f'protocol version: {protocolVersion}',
            f'subframe type: {subframe_type}',
            f'rssi={device.rssi}'
            )
        
        # if 'A' == subframe_type:
        #     # print('x as hex: ',str(service_data[10]))
        #     print(f'acc x:{ep.calc_g_units(service_data[10])} g',end='  ')
        #     print(f'acc y:{ep.calc_g_units(service_data[11])} g',end='  ')
        #     print(f'acc z:{ep.calc_g_units(service_data[12])} g')
        #     # print(f'isMoving {(service_data[15] & 0b00000011) == 1}')
            
        #     pressure = ep.calc_atmospheric_pressure(service_data[16:])
        #     print(f'pressure: {pressure/1e5} bar')
            
        #     errors = ep.get_error_codes(service_data[15])
        #     firmware_error = errors['FirmwareError']
        #     clock_error = errors['ClockError']
        #     print(f'Firmware error: {firmware_error},   clock error: {clock_error}')

        # elif 'B' == subframe_type:
        #     for axis,byte_index in zip(['x', 'y', 'z'],[10, 11, 12]):
        #         data = ep.calc_magnetic_field(service_data[byte_index])
        #         print(f'magn {axis}:{data}',end='  ')
        #     print()
            
        #     light_in_lux = ep.calc_ambient_light(service_data[13])
        #     print(f'ambient light: {light_in_lux} lx')
            
        #     uptime = ep.calc_beacon_uptime(service_data[14],service_data[15])
        #     print(f'uptime: {uptime}')
            
        #     temperature = ep.calc_ambient_temperature(service_data[15],service_data[16],service_data[17])
        #     print(f'temperature: {temperature}')

        #     battery_voltage = ep.calc_battery_voltage(service_data[17],service_data[18])
        #     print(f'battery_voltage: {battery_voltage}')

        #     battery_level = ep.calc_battery_level(service_data[19])
        #     print(f'battery_level: {battery_level}')

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