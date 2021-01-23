import sys
import datetime as dt
import asyncio
import asyncio.subprocess

from bokeh.driving import count
from bokeh.models import ColumnDataSource,DatetimeTickFormatter
from bokeh.client import push_session
from bokeh.plotting import curdoc, figure

from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

import estimote_parser.parser as ep

# Each beacon has a unique MAC Address:
# BEACON_MAC = 'C5:00:36:52:DC:DF'
BEACON_MAC = 'E0:F0:23:8C:7B:F7'

#UUID doesnt change:
ADVERTISEMENT_SERVICE_DATA_UUID = '0000fe9a-0000-1000-8000-00805f9b34fb'

def accelerometer_callback(device: BLEDevice, advertisement_data: AdvertisementData):
    if device.address == BEACON_MAC:
        # print(device.address, "RSSI:", device.rssi, advertisement_data)
        service_data = advertisement_data.service_data[ADVERTISEMENT_SERVICE_DATA_UUID]

        subframe_type = (service_data[9] & 0b00000011)
        if 0 == subframe_type:
            timestamp = dt.datetime.now()
            x = ep.calc_g_units(service_data[10])
            y = ep.calc_g_units(service_data[11])
            z = ep.calc_g_units(service_data[12])
            push(timestamp,x,y,z)


def push(timestamp, x,y,z):
    new_data = dict(
        time=[timestamp],
        x=[x],
        y=[y],
        z=[z],
        mhp=[0],
    )
    source.stream(new_data,100)

# @asyncio.coroutine
async def update():
    scanner = BleakScanner()
    scanner.register_detection_callback(accelerometer_callback)
    while True:
        await scanner.start()
        await asyncio.sleep(5)
        await scanner.stop()

source = ColumnDataSource(dict(
    time=[], x=[], y=[], z=[], mhp=[]))

# p = figure(plot_height=500, tools="xpan,xwheel_zoom,xbox_zoom,reset", x_axis_type=None, y_axis_location="right")
p = figure(
        plot_width=1400, plot_height=400,
        tools="xpan,xwheel_zoom,xbox_zoom,reset",
        x_axis_type='datetime',
        )
p.xaxis.formatter=DatetimeTickFormatter()
p.line(x='time', y='x', alpha=0.2, line_width=3, color='navy',legend_label= 'x-axis', source=source)
p.line(x='time', y='y', alpha=0.2, line_width=3, color='orange',legend_label= 'y-axis', source=source)
p.line(x='time', y='z', alpha=0.2, line_width=3, color='green',legend_label= 'z-axis', source=source)

# curdoc().add_periodic_callback(update, 50)

# open a session to keep our local document in sync with server
session = push_session(curdoc(), session_id='main')

session.show(p) # open the document in a browser

loop = asyncio.get_event_loop()
loop.run_until_complete(update())