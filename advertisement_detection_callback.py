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

logging.basicConfig()

# BEACON_MAC = 'C5:00:36:52:DC:DF'
BEACON_MAC = 'E0:F0:23:8C:7B:F7'

ADVERTISEMENT_SERVICE_DATA_UUID = '0000fe9a-0000-1000-8000-00805f9b34fb'

def twos_comp(val, bits):
    """compute the 2's complement of int value val"""
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val                         # return positive value as is

def calc_g_units(raw_acceleration):

    acceleration = twos_comp(raw_acceleration, 8)
    acceleration = int(acceleration) * 2 / 127.0
    acceleration = round(acceleration,2)

    return acceleration

def calc_magnetic_field(raw_magnetic_field):
    magnetic_field = twos_comp(raw_magnetic_field, 8)
    magnetic_field = magnetic_field / 128
    return round(magnetic_field, 2)

def calc_ambient_light(raw_light):
    ambientLightUpper = (raw_light & 0b11110000) >> 4
    ambientLightLower = raw_light & 0b00001111
    #light level in lux:
    ambientLightLevel = math.pow(2, ambientLightUpper) * ambientLightLower * 0.72

    return round(ambientLightLevel,2)

def calc_beacon_uptime(byte_14,byte_15):
    uptimeUnitCode = (byte_15 & 0b00110000) >> 4
    if 0 == uptimeUnitCode:
        uptimeUnit = 'seconds'
    elif 1 == uptimeUnitCode:
        uptimeUnit = 'minutes'
    elif 2 == uptimeUnitCode:
        uptimeUnit = 'hours'
    elif 3 == uptimeUnitCode:
        uptimeUnit = 'days'
    
    uptime = ((byte_15 & 0b00001111) << 8) | byte_14
    uptime = round(uptime,3)

    return f'{uptime} {uptimeUnit}'

def calc_ambient_temperature(byte_15,byte_16,byte_17):
    
    raw_15 = (byte_15 & 0b11000000) >> 6
    raw_16 = byte_16 << 2
    raw_17 = (byte_17 & 0b00000011) << 10
    temperatureRawValue = raw_17 | raw_16 | raw_15
        
    if temperatureRawValue > 2047 :
        #a simple way to convert a 12-bit unsigned integer to a signed one (:
        temperatureRawValue = temperatureRawValue - 4096
    temperature = temperatureRawValue / 16.0
    
    return round(temperature,2)

def calc_battery_voltage(byte_17, byte_18):
    batteryVoltage = (byte_18 << 6) | ((byte_17 & 0b11111100) >> 2)
    if batteryVoltage == 0b11111111111111: 
        batteryVoltage = 'undefined'
    return round(batteryVoltage,2)

def calc_battery_level(byte_19):
    batteryLevel = byte_19
    if batteryLevel == 0b11111111:
        batteryLevel = 'undefined'
    return batteryLevel

def accelerometer_callback(device: BLEDevice, advertisement_data: AdvertisementData):
    if device.address == BEACON_MAC:
        # print(device.address, "RSSI:", device.rssi, advertisement_data)

        service_data = advertisement_data.service_data[ADVERTISEMENT_SERVICE_DATA_UUID]
        # not_this= b'"\xbe\xd9\xccx;\x86\xde\x93\x01\xff\xff\xff\xff\x90 _\xf0%\x17'
        # not_that= b'"\xbe\xd9\xccx;\x86\xde\x93\x01\xff\xff\xff\xff\x90 `\xf0%\x17'

        subframe_type = (service_data[9] & 0b00000011)
        subframe_type = 'A' if subframe_type == 0 else 'B'
        print(device.address, dt.datetime.now().time(), f'subframe type: {subframe_type}',)
        
        if 'A' == subframe_type:
            print(f'acc x:{calc_g_units(service_data[10])} g',end='  ')
            print(f'acc y:{calc_g_units(service_data[11])} g',end='  ')
            print(f'acc z:{calc_g_units(service_data[12])} g')
            # print(f'isMoving {(service_data[15] & 0b00000011) == 1}')
        elif 'B' == subframe_type:
            for axis,byte_index in zip(['x', 'y', 'z'],[10, 11, 12]):
                data = calc_magnetic_field(service_data[byte_index])
                print(f'magn {axis}:{data}',end='  ')
            print()
            
            light_in_lux = calc_ambient_light(service_data[13])
            print(f'ambient light: {light_in_lux} lx')
            
            uptime = calc_beacon_uptime(service_data[14],service_data[15])
            print(f'uptime: {uptime}')
            
            temperature = calc_ambient_temperature(service_data[15],service_data[16],service_data[17])
            print(f'temperature: {temperature}')

            battery_voltage = calc_battery_voltage(service_data[17],service_data[18])
            print(f'battery_voltage: {battery_voltage}')

            battery_level = calc_battery_level(service_data[19])
            print(f'battery_level: {battery_level}')

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