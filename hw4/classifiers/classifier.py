class Classifier:
    """ Classifies based on sensor data and uses the current state of classifier
        Returns a state as defined in state class.
     """
    def classify(self, sensor_data):
        raise NotImplementedError()

