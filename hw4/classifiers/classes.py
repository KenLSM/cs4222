DATA_TYPES = ['a', 'b', 't', 'l', 'h']


class State:
    # Initial values
    def __init__(self):
        pass

    isFloorChange = False
    isIndoor = True
    isWalking = False

    """Can use this to set state to a number"""
    def setStateNumber(self, number):
        assert number in range(0, 8)
        self.isFloorChange = bool(number >> 2 & 1)
        self.isIndoor = bool(number >> 1 & 1)
        self.isWalking = bool(number & 1)

    """Can use this to map all states to int from 0..7 (Default state is 2)"""
    def getStateNumber(self):
        return self.isFloorChange * 4 + self.isIndoor * 2 + self.isWalking


class SensorData:
    time = None # Integer
    type = None # One of the values from DATA_TYPES
    values = None # list of values

    def __init__(self, time, type, values):
        self.time = time
        self.type = type
        self.values = values