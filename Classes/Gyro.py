import smbus
from mpu6050 import mpu6050
import time
import math

PWR_M = 0x6B
DIV = 0x19
CONFIG = 0x1A
GYRO_CONFIG = 0x1B
INT_EN = 0x38
ACCEL_X = 0x3B
ACCEL_Y = 0x3D
ACCEL_Z = 0x3F
GYRO_X = 0x43
GYRO_Y = 0x45
GYRO_Z = 0x47
TEMP = 0x41

bus = smbus.SMBus(1)


class Gyro:
  def __init__(self, address=0x68, calibrate=True, ax=0, ay=0, az=0, gx=0, gy=0, gz=0):
    self.Device_Address = 0x68   # device address
    # self.mpu = mpu6050(self.Device_Address)
    self.caliibrate = calibrate
    self.AxCal = (0, ax)[calibrate == False]
    self.AyCal = (0, ay)[calibrate == False]
    self.AzCal = (0, az)[calibrate == False]
    self.GxCal = (0, gx)[calibrate == False]
    self.GyCal = (0, gy)[calibrate == False]
    self.GzCal = (0, gz)[calibrate == False]

    bus.write_byte_data(self.Device_Address, DIV, 7)
    bus.write_byte_data(self.Device_Address, PWR_M, 1)
    bus.write_byte_data(self.Device_Address, CONFIG, 0)
    bus.write_byte_data(self.Device_Address, GYRO_CONFIG, 24)
    bus.write_byte_data(self.Device_Address, INT_EN, 1)
    time.sleep(1)

  def calibrate(self, precision=200):
    print("Calibrating", end='')
    x = 0
    y = 0
    z = 0
    xang = 0
    yang = 0
  

    for i in range(precision):
        x = (self.readMPU(ACCEL_X)/16384.0)
        y = (self.readMPU(ACCEL_Y)/16384.0)
        z = z + (self.readMPU(ACCEL_Z)/16384.0)
        zang = (self.readMPU(ACCEL_Z)/16384.0)
        xang = xang + Gyro.GetXRotation(x,y,zang)
        yang = yang + Gyro.GetYRotation(x,y,zang)
        print('.',end='')
    x = xang/precision
    y = yang/precision
    z = z/precision
    self.AxCal = x
    self.AyCal = y
    self.AzCal = z

    x = 0
    y = 0
    z = 0
    for i in range(precision):
        x = x + (self.readMPU(GYRO_X)/131.0)
        y = y + (self.readMPU(GYRO_Y)/131.0)
        z = z + (self.readMPU(GYRO_Z)/131.0)
        print('.',end='')
    x = x/precision
    y = y/precision
    z = z/precision
    self.GxCal = x
    self.GyCal = y
    self.GzCal = z

    print('done!')
    return {
        'accel': {"x": self.AxCal, "y": self.AyCal, "z": self.AzCal},
        'gyro': {"x": self.GxCal, "y": self.GyCal, "z": self.GzCal}
    }

  def readMPU(self, addr):
    high = bus.read_byte_data(self.Device_Address, addr)
    low = bus.read_byte_data(self.Device_Address, addr+1)
    value = ((high << 8) | low)
    if (value > 32768):
        value = value - 65536
    return value

  def accel(self):
    x = self.readMPU(ACCEL_X)
    y = self.readMPU(ACCEL_Y)
    z = self.readMPU(ACCEL_Z)
    Ax = (x/16384.0-self.AxCal)
    Ay = (y/16384.0-self.AyCal)
    Az = (z/16384.0-self.AzCal)
    time.sleep(.01)
    return {'x': Ax, 'y': Ay, 'z': Az}
    # return self.mpu.get_accel_data()

  def gyro(self):
    x = self.readMPU(GYRO_X)
    y = self.readMPU(GYRO_Y)
    z = self.readMPU(GYRO_Z)
    Gx = x/131.0 - self.GxCal
    Gy = y/131.0 - self.GyCal
    Gz = z/131.0 - self.GzCal
    time.sleep(.01)
    return {'x': Gx, 'y': Gy, 'z': Gz}
    # return self.mpu.get_gyro_data()
  
  @staticmethod
  def GetYRotation(x, y, z):
      radians = math.atan2(x, Gyro.dist(y, z))
      return -math.degrees(radians)
  
  @staticmethod
  def GetXRotation(x, y, z):
      radians = math.atan2(y, Gyro.dist(x, z))
      return math.degrees(radians)

  @staticmethod
  def dist(a, b):
      return math.sqrt((a * a) + (b * b))

  def temp(self):
      tempRow = self.readMPU(TEMP)
      tempC = (tempRow / 340.0) + 36.53
      tempC = "%.2f" % tempC
      time.sleep(.2)
      return tempC#self.mpu.get_temp()#tempC


print("MPU6050 Interface")
print("Circuit Digest")
time.sleep(2)
gyro = Gyro()
cal = gyro.calibrate()
print("Calibrating values:")
print(cal)
print('++++++++++++++++')
while 1:
  for i in range(20):
      temp = gyro.temp()
      accel = gyro.accel()
      g = gyro.gyro()
      xrot = Gyro.GetXRotation(g['x'],g['y'],g['z'])
      yrot = Gyro.GetYRotation(g['x'],g['y'],g['z'])
      # print(f"Temp: {temp}c")
      # print(f"accelerometer: x:{accel['x']}, y:{accel['y']}, z:{accel['z']}")
      print(f"gyro angle: x:{g['x']}, y:{g['y']}, z:{g['z']} - x angle: {xrot}, y angle: {yrot}")
      print('===========')
      time.sleep(1)
