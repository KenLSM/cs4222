from scipy import stats

from .classifier import Classifier
from .classes import State


def pow2(a):
    return a ** 2


def minus(l, r):
    return [i - j for i, j in zip(l, r)]


# Idle ? WALKING
# Idea 1:
# Change is a lot when WALKING
# Compare value with previous, sum of moving average, do threshold.
# The culmulative average weighted to the latest data
# Define window.
WALK_DIM_FACTOR = 0.95  # at 50th element, it will take 7.6% of its original value
SWITCH_2_WALK_THRESHOLD = 0.3
SWITCH_2_IDLE_THRESHOLD = 0.1

# FLOOR CHANGE
# Idea:
# Will have change in barometer values
# Compare value with previous, sum of moving average, do threshold.
# Barometer can jump around, which usually doens't make sense, will need to damp it down
FLOOR_WINDOW_SIZE = 20
BARO_DAMP_THRESHOLD = 0.2
BARO_DAMP_FACTOR = 0.00001
SWITCH_2_CHANGE_FLOOR_THRESHOLD = 3e-5
SWITCH_2_NO_FLOOR_THRESHOLD = 5e-6

# Indoor - Outdoor
# Idea:
# Outdoor have way higher values
# Simple average and thresholding
IODOOR_WINDOW_SIZE = 20
LIGHT_DAMP_THRESHOLD = 100
LIGHT_DAMP_FACTOR = 1
SWITCH_2_OUTDOOR_THRESHOLD = 150
SWITCH_2_INDOOR_THRESHOLD = 50


class StateMachineClassifier(Classifier):
    prev_a = None
    moving_a_delta = None
    _state = None

    def __init__(self, window_size=1000):
        self.prev_a = []
        self.baro_data = []
        self.baro_time = []
        self.light_data = []
        self.moving_a_delta = .0

        self._state = State()
        self.counter = 0
        pass

    def classify(self, sensor_datas):
        for sensor_data in sensor_datas:
            self.classify_single_data(sensor_data)

    def decide_moving_state(self, sensor_data, delta_sum):
        if self._state.isWalking:
            if self.moving_a_delta < SWITCH_2_IDLE_THRESHOLD:
                self._state.setStateNumber(self._state.getStateNumber() & int(0b110))  # toggle to idle
                print('IDLE. Time: {:8d} Avg: {:.6} Sum: {:.6}'.format(
                    sensor_data.time, self.moving_a_delta, delta_sum))
            return
        if self.moving_a_delta > SWITCH_2_WALK_THRESHOLD:
            self._state.setStateNumber(self._state.getStateNumber() | int(0b001))  # toggle to walking
            print('WALK. Time: {:8d} Avg: {:.6} Sum: {:.6}'.format(
                sensor_data.time, self.moving_a_delta, delta_sum))

    def decide_floor_state(self, sensor_data):
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            self.baro_time[-FLOOR_WINDOW_SIZE:], self.baro_data[-FLOOR_WINDOW_SIZE:])
        if self._state.isFloorChange:
            if abs(slope) < SWITCH_2_NO_FLOOR_THRESHOLD:
                self._state.setStateNumber(self._state.getStateNumber() & int(0b011))  # toggle to no floor change
                print('FLNO. Time: {:8d} Slope: {:.8f}'.format(
                    sensor_data.time, abs(slope)))
            return
        if abs(slope) > SWITCH_2_CHANGE_FLOOR_THRESHOLD:
            self._state.setStateNumber(self._state.getStateNumber() | int(0b100))  # toggle to no floor change
            print('FLCH. Time: {:8d} Slope: {:.8f}'.format(
                sensor_data.time, abs(slope)))

    def decide_iodoor_state(self, sensor_data):
        avg_l = sum(self.light_data[-IODOOR_WINDOW_SIZE:]) / len(self.light_data[-IODOOR_WINDOW_SIZE:])
        # print(avg_l)
        if self._state.isIndoor:
            if avg_l > SWITCH_2_OUTDOOR_THRESHOLD:
                self._state.setStateNumber(self._state.getStateNumber() & int(0b101))  # toggle to no floor change
                print('OTDR. Time: {:8d} Average: {:.8f}'.format(
                    sensor_data.time, avg_l))
            return
        if avg_l < SWITCH_2_INDOOR_THRESHOLD:
            self._state.setStateNumber(self._state.getStateNumber() | int(0b010))  # toggle to no floor change
            print('INDR. Time: {:8d} Average: {:.8f}'.format(
                sensor_data.time, avg_l))

    def classify_single_data(self, sensor_data):
        self.counter += 1
        if sensor_data._type == 'a':
            cur_a = sensor_data.values
            delta_v = minus(cur_a, self.prev_a)
            delta_sum = sum(map(pow2, delta_v))
            self.prev_a = cur_a
            self.moving_a_delta = self.moving_a_delta * WALK_DIM_FACTOR + delta_sum
            self.decide_moving_state(sensor_data, delta_sum)

            return
        if sensor_data._type == 'b':
            cur_b = sensor_data.values
            try:
                delta_b = cur_b[0] - self.baro_data[-1]
                if delta_b > BARO_DAMP_THRESHOLD and self.baro_data[-1]:
                    cur_b = [self.baro_data[-1] + delta_b * BARO_DAMP_FACTOR]
            except IndexError:  # initial entry
                pass
            self.baro_data += cur_b
            self.baro_time += [sensor_data.time]

            self.decide_floor_state(sensor_data)

            return

        if sensor_data._type == 'l':
            cur_l = sensor_data.values
            try:
                delta_l = cur_l[0] - self.light_data[-1]
                if delta_l > LIGHT_DAMP_THRESHOLD and self.light_data[-1]:
                    cur_l = [self.light_data[-1] + delta_l * LIGHT_DAMP_FACTOR]
            except IndexError:  # initial entry
                pass
            self.light_data += cur_l

            self.decide_iodoor_state(sensor_data)

            return
        # raise Exception('IDK WHAT TO DO WITH THIS INPUT: ' + sensor_data)
