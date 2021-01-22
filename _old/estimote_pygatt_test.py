import pygatt

# The BGAPI backend will attempt to auto-discover the serial device name of the
# attached BGAPI-compatible USB adapter.
adapter = pygatt.BGAPIBackend()
# adapter = pygatt.backends.GATTToolBackend()
adapter = pygatt.BGAPIBackend(serial_port='COM12')
address = "C5:00:36:52:DC:DF"

try:
    adapter.start()
    device = adapter.connect(address)
    print(dir(device))
    # value = device.char_read("a1e8f5b1-696b-4e4c-87c6-69dfe0b0093b")
finally:
    adapter.stop()