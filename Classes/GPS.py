import serial
import time
import string
import pynmea2
import io
from fastapi_utils.tasks import repeat_every
from Classes.MyEventHandler import MyEventHandler
from pprint import pprint

port = '/dev/serial0'
baud = 9600
lat = None
lon = None
Disable_GPGSV = ['0xB5', '0x62', '0x06', '0x01', '0x03', '0x00', '0xF0', '0x03', '0x00', '0xFD', '0x15']

class GPS:
    def __init__(self, eventHandler:MyEventHandler, port:str='/dev/serial0', baud:int=9600):
        self.port = port
        self.baudrate = baud
        self.lat = None
        self.lon = None
        self.lat_dir = None
        self.lon_dir = None
        self.speed = 0
        self.alt = None
        self.alt_unit = None
        self.num_sats = 0
        self.eventHandler = eventHandler
        self.readGPSData()
        
        self.ser=serial.Serial(port, baudrate=9600, timeout=0.5)
        self.sio = io.TextIOWrapper(io.BufferedRWPair(self.ser, self.ser))
        self.sio.writelines(','.join(Disable_GPGSV))

    async def readGPSData(self):
        try:
            # port="/dev/ttyAMA0"
            # self.ser=serial.Serial(port, baudrate=9600, timeout=0.5)
            # self.sio = io.TextIOWrapper(io.BufferedRWPair(self.ser, self.ser))
            for x in range(0,1):
                if self.sio.readable() == True:
                    # dataout = pynmea2.NMEAStreamReader()
                    newdata=self.sio.readline()#.readline()#.decode('utf-8')
                    if newdata[0:6] == "$GNRMC" or newdata[0:6] == "$GNGGA":#"$GNRMC|GPGGA":
                        newmsg=pynmea2.parse(newdata)
                        self.lat=newmsg.lat#itude
                        self.lat_dir = newmsg.lat_dir
                        self.lon=newmsg.lon#gitude
                        self.lon_dir = newmsg.lon_dir
                        try:
                            #extra data
                            if newdata[0:6] == "$GNRMC":
                                self.speed=newmsg.spd_over_grnd
                            if newdata[0:6] == "$GNGGA":
                                self.num_sats=newmsg.num_sats
                                self.alt = newmsg.altitude
                                self.alt_unit=newmsg.altitude_units
                        except Exception as e1:
                            print(f"Extra GPS data error: {e1}")
                        pprint(repr(newmsg))
                        # gps = "Latitude=" + str(self.lat) + " and Longitude=" + str(self.lon)  + f"{self.speed}:{self.alt}"
                        self.eventHandler.trigger('GPS_CHANGED', {'lat': self.lat, 'lon': self.lon, 'alt': self.alt, 'alt_unit': self.alt_unit, 'sats': self.num_sats, 'speed': self.speed})
                        # print(gps)
                # time.sleep(0.1)
        except Exception as e:
            print(f"reconnecting Error: {e}")
            self.ser=serial.Serial(port, baudrate=9600, timeout=0.5)
            self.sio = io.TextIOWrapper(io.BufferedRWPair(self.ser, self.ser))
