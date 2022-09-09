import pigpio
pi = pigpio.pi()
from Classes.Tools import Tools

import os
print("Initializing pigpiod...", end='')
os.system('sudo pigpiod')
print('done!')

class MyServo:
    def __init__(self, pin:int, min_pulse:int=1000, max_pulse:int=2000):
        self.pin = pin
        self.min_pulse = min_pulse
        self.max_pulse = max_pulse

    def write(self, angle):
        value = Tools.map(angle, 1000,2000, self.min_pulse, self.max_pulse)
        # print(f"mapped value: {value}")
        value = Tools.map(value, 1000,2000, 500, 2500)
        # print(f"pulse: {value}")
        pi.set_servo_pulsewidth(self.pin, value)

    def destroy(self):
        print('Stopping pigpio')
        pi.stop()