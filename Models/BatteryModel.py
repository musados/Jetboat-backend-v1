class Battery:
    def __init__(self, rxpin:int, txpin:int):
        self.rx =rxpin
        self.tx = txpin
        self.voltage = 0
        #settings
        self.ampHour = -1
        self.minVoltage = -1
        self.maxVoltage = -1