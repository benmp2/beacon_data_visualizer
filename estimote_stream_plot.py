import sys
import datetime as dt
import asyncio
import asyncio.subprocess
import math
import statistics

from bokeh.driving import count
from bokeh.models import ColumnDataSource,DatetimeTickFormatter
from bokeh.client import push_session
from bokeh.plotting import curdoc, figure
from bokeh.layouts import row,column
from bokeh.models import HoverTool

from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

import estimote_parser.parser as ep

# import ctypes
# screen_width = ctypes.windll.user32.GetSystemMetrics(0)
# screen_height = ctypes.windll.user32.GetSystemMetrics(1)
screen_height = 600
screen_width = 1200

MAX_WIDTH = math.floor(96 * screen_width / 100)  # buffer to adjust
MAX_HEIGHT = math.floor(85 * screen_height / 100)
HALF_MAX_HEIGHT = math.floor(MAX_HEIGHT / 2)

# Each beacon has a unique MAC Address:
# BEACON_MAC = 'C5:00:36:52:DC:DF'
BEACON_MAC = 'E0:F0:23:8C:7B:F7'

#UUID doesnt change:
ADVERTISEMENT_SERVICE_DATA_UUID = '0000fe9a-0000-1000-8000-00805f9b34fb'


# class accelerometer_callback():
buffer_size = 8
mhp_buffer={'timestamp':[0]*buffer_size,
            'x':[0]*buffer_size,
            'y':[0]*buffer_size,
            'z':[0]*buffer_size
            }



def push_to_mhp_buffer(timestamp,x,y,z):
    global mhp_buffer
    
    mhp_buffer['timestamp'].append(timestamp)
    mhp_buffer['x'].append(x)
    mhp_buffer['y'].append(y)
    mhp_buffer['z'].append(z)


    for key in mhp_buffer:
        mhp_buffer[key] = mhp_buffer[key][1:]

    # #determine buffer size for mhp feature
    # if len(mhp_buffer['timestamp']) > buffer_size:
    #     for key in mhp_buffer:
    #         mhp_buffer[key] = mhp_buffer[key][1:]

def calculate_mhp_feature(timestamp,x,y,z):
    global mhp_buffer

    if len(mhp_buffer['timestamp']) == buffer_size:
        x_mhp = (x - statistics.mean(mhp_buffer['x']))**2
        y_mhp = (y - statistics.mean(mhp_buffer['y']))**2
        z_mhp = (z - statistics.mean(mhp_buffer['z']))**2
    else:
        x_mhp,y_mhp,z_mhp = 0,0,0

    return statistics.sqrt(x_mhp+y_mhp+z_mhp)

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
            push_to_mhp_buffer(timestamp,x,y,z)
            mhp = calculate_mhp_feature(timestamp,x,y,z)
            # mhp=0
            push(timestamp,x,y,z,mhp)


def push(timestamp, x,y,z,mhp):
    new_data = dict(
        time=[timestamp],
        x=[x],
        y=[y],
        z=[z],
        mhp=[mhp],
    )
    source.stream(new_data,100)

# @asyncio.coroutine
async def update():
    scanner = BleakScanner(filter={'DuplicateData':False})
    scanner.register_detection_callback(accelerometer_callback)
    while True:
        await scanner.start()
        await asyncio.sleep(5)
        await scanner.stop()

source = ColumnDataSource(dict(
    time=[], x=[], y=[], z=[], mhp=[]))


# p = figure(plot_height=500, tools="xpan,xwheel_zoom,xbox_zoom,reset", x_axis_type=None, y_axis_location="right")
p1 = figure(
        plot_width=MAX_WIDTH, plot_height=400,
        tools="xpan,xwheel_zoom,xbox_zoom,reset",
        x_axis_type='datetime',
        )
p1.xaxis.formatter=DatetimeTickFormatter()
p1.line(x='time', y='x', alpha=0.2, line_width=3, color='navy',legend_label= 'x-axis', source=source)
p1.line(x='time', y='y', alpha=0.2, line_width=3, color='orange',legend_label= 'y-axis', source=source)
p1.line(x='time', y='z', alpha=0.2, line_width=3, color='green',legend_label= 'z-axis', source=source)


hover = HoverTool(tooltips=[('date', '@x{%H:%M:%S}')],
          formatters={'@x': 'datetime'})

p2 = figure(
        plot_width=MAX_WIDTH, plot_height=HALF_MAX_HEIGHT,
        tools="xpan,xwheel_zoom,xbox_zoom,reset",
        x_axis_type='datetime'
        )
p2.xaxis.formatter=DatetimeTickFormatter()
p2.line(x='time', y='mhp', alpha=0.2, line_width=3, color='navy',legend_label= 'mhp feature', source=source)
p2.circle(x='time', y='mhp', fill_color="white",size=8, source=source)
p2.add_tools(hover)
p = column(p1, p2)

# open a session to keep our local document in sync with server
session = push_session(curdoc(), session_id='main')

session.show(p) # open the document in a browser

loop = asyncio.get_event_loop()
loop.run_until_complete(update())