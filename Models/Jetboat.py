
import time
import sys
import json
from pydantic import BaseModel
from Classes.MyServo import MyServo
from Classes.read_RPM import reader
import RPi.GPIO as GPIO
import os
os.system('sudo pigpiod')
from Classes.AnalogDevice import *
from Classes.Thermistor import *
from Classes.Tools import Tools
from Classes.Gyro2 import IMU as Gyro
from Classes.MyEventHandler import MyEventHandler
from gpiozero import CPUTemperature



GPIO.setmode(GPIO.BCM)

# gyro = Gyro()

servoPin = 27
escPin = 17
motorThermPin = 0
boatThermPin = 1
waterSensPin = 2
raspThermPin = 3

# servo_min = int(Tools.map(30, 0,180, 1000,2000))
# servo_max = int(Tools.map(130, 0,180, 1000,2000))
# print(servo_min)
# print(servo_max)
# servo = MyServo(servoPin, servo_min, servo_max)
# motor_min = int(Tools.map(1000, 500,2500, 1000,2000))
# motor_max = int(Tools.map(2000, 500,2500, 1000,2000))
# motor = MyServo(escPin,motor_min,motor_max)


# waterSens = AnalogDevice(2)
# rasptherm = Thermistor(3)
# boattherm = Thermistor(1)
# motortherm = Thermistor(0)

class JetboatParameters(BaseModel):
    motorPin:int
    servoPin:int
    # thermistors
    motorThermPin:int
    boatThermPin:int
    raspThermPin:int
    #sensors
    waterSensPin:int


class Jetboat:
    def __init__(self, boatParams:JetboatParameters, eventHandler: MyEventHandler):
        self.eventHandler = eventHandler
        self.cpu = CPUTemperature()
        # motor init
        self.motorPin = boatParams.motorPin
        self.motorMin = int(Tools.map(1000, 500,2500, 1000,2000))
        self.motorMax = int(Tools.map(2000, 500,2500, 1000,2000))
        self.motor = MyServo(self.motorPin, self.motorMin, self.motorMax)

        # Servo init
        self.servoPin = boatParams.servoPin
        self.servoMin = int(Tools.map(30, 0,180, 1000,2000))
        self.servoMax = int(Tools.map(130, 0,180, 1000,2000))
        print(self.servoMin)
        print(self.servoMax)
        self.servo = MyServo(self.servoPin, self.servoMin, self.servoMax)
        self.servo.write(1500)

        # Gyro
        self.gyro = Gyro()
        self.gyro.Error_value_accel_data,self.gyro.Error_value_gyro_data=self.gyro.average_filter()

        # Sensors
        self.motorThermPin = boatParams.motorThermPin
        self.motorTherm = Thermistor(self.motorThermPin)

        self.boatThermPin = boatParams.boatThermPin
        self.boatTherm = Thermistor(self.boatThermPin)

        self.raspThermPin = boatParams.raspThermPin
        self.raspTherm = Thermistor(self.raspThermPin)

        self.waterSensPin = boatParams.waterSensPin
        self.waterSens = AnalogDevice(self.waterSensPin)

        # Values
        self.cpuTemp = self.cpu.temperature
        self.motorTemp = -1
        self.boatTemp = -1
        self.raspTemp = -1
        self.waterSensValue = -1
        self.roll,self.pitch,self.yaw = (-1, -1, -1)
        self.steeringValue = 1500
        self.gasValue = 1500

        self.lastControlCommand = 0
        self.lastSensorReaded = 0
        print("Boat initialized! :)")

    def initMotor(self):
        # init the motor
        motor.write(2000)
        time.sleep(2)
        motor.write(1000)
        time.sleep(2)
        motor.write(1500)
        time.sleep(2)
    
    def readGyro(self):
        result = self.gyro.imuUpdate()
        return result

    def triggerEvent(self, eventname:str, data):
        print('triggerEvent')
        if self.eventHandler:
            try:
                self.eventHandler.trigger('SensorsChanged', data)
            except Exception as e:
                print(e)

    def steer(self, value:int = 1500):
        if value < 1000:
            value = 1000
        if value > 2000:
            value = 2000
        self.steeringValue = value
        self.servo.write(value)

    def move(self, value:int = 1500):
        if value < 1000:
            value = 1000
        if value > 2000:
            value = 2000
        self.gasValue = value
        self.motor.write(value)
    
    def control(self, moveval:int, steeringval:int):
        self.lastControlCommand = time.time()
        # self.move(moveval)
        self.steer(steeringval)
    
    def getSensorsDict(self):
        return json.dumps({
            # temp
            'temperature':{
                'cpu':self.cpuTemp,
                'motor':self.motorTemp,
                'boat':self.boatTemp,
                'raspberry':self.raspTemp,
            },
            # gyro
            'gyro': {
                'roll': self.roll,
                'pitch':self.pitch,
                'yaw': self.yaw
            },
            # water
            'water': {
                'main': self.waterSensValue
            },
            'battery':{}, # to be implemented!
            'gps':{
                'latitude':None,
                'longtitude':None,
                'altitude':None,
                'satellites':0,
                'fix':False,
            }
        })
    
    def readAllSensors(self):
        nowTime = time.time()
        if self.lastSensorReaded == 0 or (nowTime - self.lastSensorReaded) >= 0.01: 
            print('Reading sensors...', end='')
            self.cpuTemp = self.cpu.temperature
            self.motorTemp = self.motorTherm.readTemp()
            self.boatTemp = self.boatTherm.readTemp()
            self.raspTemp = self.raspTherm.readTemp()
            self.waterSensValue = self.waterSens.read()
            self.roll,self.pitch,self.yaw = self.gyro.imuUpdate()
            print(f'done! interval: {time.time() - nowTime}')
            self.lastSensorReaded = nowTime
            self.triggerEvent('SensorsChanged', self.getSensorsDict())
    
    def printAllSensors(self):
        print("\n===============\n   Sensors\n===============")
        print(f"CPU temp: {self.cpuTemp}")
        print(f"Motor temp: {self.motorTemp}")
        print(f"Boat temp: {self.boatTemp}") 
        print(f"Raspberry temp: {self.raspTemp}") 
        print(f"Water level: {self.waterSensValue}") 
        print(f"Roll: {self.roll}, Pitch: {self.pitch}, Yaw: {self.yaw}\n")

    
    def loopTask(self):
        nowTime = time.time()
        if (nowTime - self.lastControlCommand) > 1:
            print('timeoutddd')
            print(f"steering: {self.steeringValue}, gas: {self.gasValue}")
            # self.move()
            self.steer()
        
        self.readAllSensors()
        self.printAllSensors()

    def destroy(self):
        # poten.destroy()
        self.servo.destroy()
        GPIO.cleanup()
