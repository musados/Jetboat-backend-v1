from Classes.ADCDevice import *
#adc = ADCDevice() # Define an ADCDevice class object


class AnalogDevice:
    def __init__(self, pin:int):
        self.adc = ADCDevice()
        if(self.adc.detectI2C(0x48)): # Detect the pcf8591.
            self.adc = PCF8591()
        elif(self.adc.detectI2C(0x4b)): # Detect the ads7830
            self.adc = ADS7830()
        else:
            print("No correct I2C address found, \n"
            "Please use command 'i2cdetect -y 1' to check the I2C address! \n"
            "Program Exit. \n")
            exit(-1)
        self.pin = pin

    def read(self):
        return self.adc.analogRead(self.pin)
    
    def destroy(self):
        self.adc.close()
