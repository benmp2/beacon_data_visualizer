test_data = b'"\xbe\xd9\xccx;\x86\xde\x93\x00\xfe\x00\xc1DF\xf9\xff\xff\xff\xff'
# test_data = b'"\xbe\xd9\xccx;\x86\xde\x93\x01\xff\xff\xff\xff\x90 ^\xf0%\x17'

for i,data in enumerate(test_data):    
    if i == 0:
        print('ESTIMOTE_FRAME_TYPE_TELEMETRY:', data & 0b00001111)
        print('protocolVersion: ', ((data & 0b11110000) >> 4))
    if i == 9:
        subframe_type = (data & 0b00000011)
        print('Telemetry subframe type', subframe_type)

print(test_data[9:10], (test_data[9] & 0b00000011))
print(test_data[10:11], (int(test_data[10]) * 2 / 127.0))
print(test_data[11:12], (int(test_data[11]) * 2 / 127.0))
print(test_data[12:13], (int(test_data[12]) * 2 / 127.0))
    