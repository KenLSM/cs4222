class Classifier:
    """ Classifies based on a list of sensor data for 1 time step
        and uses the current state of classifier to return a prediction.
        Returns a state as defined in state class.
     """
    def classify(self, sensor_datas):
        raise NotImplementedError()

