
import time
from MyServo import MyServo
from read_RPM import reader
import RPi.GPIO as GPIO
import os
# os.system('sudo pigpiod')
from AnalogDevice import *
from Thermometer import *
from Tools import Tools



GPIO.setmode(GPIO.BCM)

servoPin = 18
escPin = 17

servo_min = int(Tools.map(30, 0,180, 1000,2000))
servo_max = int(Tools.map(130, 0,180, 1000,2000))
print(servo_min)
print(servo_max)
servo = MyServo(servoPin, servo_min, servo_max)
motor_min = int(Tools.map(1000, 500,2500, 1000,2000))
motor_max = int(Tools.map(2000, 500,2500, 1000,2000))
motor = MyServo(escPin,motor_min,motor_max)


therm = Thermistor(1)
poten = AnalogDevice(0)

def setup():
    print(f"temp init: {therm.readTemp()}")
    print(f"Potentiometer init: {poten.read()}")

    # init the motor
    motor.write(2000)
    time.sleep(2)
    motor.write(1000)
    time.sleep(2)
    motor.write(1500)
    time.sleep(2)

def loop():
    while True:
        potVal = poten.read()
        srvVal = Tools.map(potVal, 0,255,1000,2000)
        servo.write(srvVal)

        print ('Potentiometer Value : %d, Voltage : %.2f, Temperature : %.2f'%(poten.read(),3.3,therm.readTemp()))
        time.sleep(0.01)


def destroy():
    poten.destroy()
    servo.destroy()
    GPIO.cleanup()

if __name__ == '__main__': # Program entrance
    print ('Program is starting ... ')
    setup()
    try:
        loop()
    except KeyboardInterrupt: # Press ctrl-c to end the program.
        destroy()

