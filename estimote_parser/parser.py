import math 
import struct

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

def calc_atmospheric_pressure(pressure_bytes):
    # atmospheric pressure in pascals (Pa)
    print(pressure_bytes.hex('-'))

    pressure = struct.unpack('<I', pressure_bytes)[0] / 256.0
    return round(pressure,2)

def get_error_codes(byte_15):
    hasFirmwareError = ((byte_15 & 0b00000100) >> 2) == 1
    hasClockError = ((byte_15 & 0b00001000) >> 3) == 1

    return {'FirmwareError' : hasFirmwareError,
            'ClockError' : hasClockError,
            }