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

    def __repr__(self):
        return 'floorChange: %s indoor: %s walking: %s' % (self.isFloorChange, self.isIndoor, self.isWalking)


class SensorData:
    time = None  # Integer
    _type = None  # One of the values from DATA_TYPES
    values = None  # list of values

    def __init__(self, time, _type, values):
        assert type(values) is list, 'values is not list'
        assert _type in DATA_TYPES, '_type is unknown'
        self.time = time
        self._type = _type
        self.values = values

    def __repr__(self):
        return '%s,%s,%s,%s,%s' \
               % (self.time,
                  self._type,
                  self.sanitize_output(self.values, 0),
                  self.sanitize_output(self.values, 1),
                  self.sanitize_output(self.values, 2))

    def sanitize_output(self, values, idx):
        if idx >= len(values):
            return ''
        else:
            return values[idx]
