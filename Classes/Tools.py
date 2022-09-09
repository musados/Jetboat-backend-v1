class Tools:
    @staticmethod
    def map(value, fromLow, fromHigh, toLow, toHigh): # map a value from one range to another range
            if value < fromLow:
                value = fromLow
            if value > fromHigh:
                value = fromHigh
            return (toHigh-toLow)*(value-fromLow) / (fromHigh-fromLow) + toLow
            
    @staticmethod
    def servo_map(value, fromLow, fromHigh): # map a value from one range to another range
        toLow = -1.0
        toHigh = 1.0
        if value < fromLow:
            value = fromLow
        if value > fromHigh:
            value = fromHigh
        valPerc = ((value - fromLow) * 100) / (fromHigh-fromLow)
        print(str(valPerc) + '%')
        res = (toHigh-toLow) * (valPerc/100)
        print(str(res) + ' ll')
        res = (res + toLow)
        print(res)
        return res