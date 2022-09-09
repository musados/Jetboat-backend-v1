import RPi.GPIO as GPIO
import time
import math
# from ADCDevice import *
# adc = ADCDevice() # Define an ADCDevice class object
from Classes.AnalogDevice import AnalogDevice


class Thermistor(AnalogDevice):
    def __init__(self, pin:int):
        super().__init__(pin)

    def readTemp(self, kelvin = False):
        value = self.read()
        print(value)
        voltage = value / 255.0 * 3.3 # calculate voltage
        print(voltage)
        Rt = 10 * voltage / (3.3 - voltage) # calculate resistance value of thermistor
        tempK = 1/(1/(273.15 + 25) + math.log(Rt/10)/3950.0) # calculate temperature (Kelvin)
        tempC = tempK -273.15 # calculate temperature (Celsius)
        if kelvin == True:
            return tempK
        return tempC
