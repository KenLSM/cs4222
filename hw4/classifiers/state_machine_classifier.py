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

BARO_DAMP_THRESHOLD = 0.2
BARO_DAMP_FACTOR = 0.00001
SWITCH_2_CHANGE_FLOOR_THRESHOLD = 3e-5
SWITCH_2_NO_FLOOR_THRESHOLD = 5e-6

# Indoor - Outdoor
# Idea:
# Outdoor have way higher values
# Simple average and thresholding

LIGHT_DAMP_THRESHOLD = 100
LIGHT_DAMP_FACTOR = 1
SWITCH_2_OUTDOOR_THRESHOLD = 250
SWITCH_2_INDOOR_THRESHOLD = 50

DEBUG = False

STR_WALK = '%s,WALKING'
STR_IDLE = '%s,IDLE'
STR_FLCH = '%s,FLOORCHANGE'
STR_FLNO = '%s,NOFLOORCHANGE'
STR_INDR = '%s,INDOOR'
STR_OUDR = '%s,OUTDOOR'

DELAY_TIME = 10000

FIXED_VAL = 10000  # 10 seconds window


class StateMachineClassifier(Classifier):
    prev_a = None
    moving_a_delta = None
    _state = None

    def __init__(self, window_size=1000):
        self.prev_a = []
        self.moving_a_delta = .0

        self.baro_data = []
        self.baro_time = []

        self.light_data = []
        self.light_time = []

        self.io_last_change = 0
        self.fl_last_change = 0
        self.wl_last_change = 0

        self._state = State()
        self.counter = 0
        pass

    def classify(self, sensor_datas):
        for sensor_data in sensor_datas:
            self.classify_single_data(sensor_data)

    def decide_moving_state(self, sensor_data, delta_sum):
        if self.wl_last_change + DELAY_TIME > sensor_data.time:
            return

        if self._state.isWalking:
            if self.moving_a_delta < SWITCH_2_IDLE_THRESHOLD:
                self._state.setStateNumber(self._state.getStateNumber() & int(0b110))  # toggle to idle
                if DEBUG:
                    print('IDLE. Time: {:8d} Avg: {:.6} Sum: {:.6}'.format(
                        sensor_data.time, self.moving_a_delta, delta_sum))
                print(STR_IDLE % sensor_data.time)
                self.wl_last_change = sensor_data.time
            return

        if self.moving_a_delta > SWITCH_2_WALK_THRESHOLD:
            self._state.setStateNumber(self._state.getStateNumber() | int(0b001))  # toggle to walking
            if DEBUG:
                print('WALK. Time: {:8d} Avg: {:.6} Sum: {:.6}'.format(
                    sensor_data.time, self.moving_a_delta, delta_sum))
            print(STR_WALK % sensor_data.time)
            self.wl_last_change = sensor_data.time

    def decide_floor_state(self, sensor_data):
        if self.fl_last_change + DELAY_TIME > sensor_data.time:
            return

        #  only take last X seconds ago
        time_filtered = list(filter(lambda x: x > (sensor_data.time - FIXED_VAL), self.baro_time))

        slope, intercept, r_value, p_value, std_err = stats.linregress(
            time_filtered, self.baro_data[-len(time_filtered):])

        if self._state.isFloorChange:
            if abs(slope) < SWITCH_2_NO_FLOOR_THRESHOLD:
                self._state.setStateNumber(self._state.getStateNumber() & int(0b011))  # toggle to no floor change
                if DEBUG:
                    print('FLNO. Time: {:8d} Slope: {:.8f}'.format(
                        sensor_data.time, abs(slope)))
                print(STR_FLNO % sensor_data.time)
                self.fl_last_change = sensor_data.time
            return

        if abs(slope) > SWITCH_2_CHANGE_FLOOR_THRESHOLD:
            self._state.setStateNumber(self._state.getStateNumber() | int(0b100))  # toggle to no floor change
            if DEBUG:
                print('FLCH. Time: {:8d} Slope: {:.8f}'.format(
                    sensor_data.time, abs(slope)))
            print(STR_FLCH % sensor_data.time)
            self.fl_last_change = sensor_data.time

    def decide_iodoor_state(self, sensor_data):
        if self.io_last_change + DELAY_TIME > sensor_data.time:
            return

        time_filtered = list(filter(lambda x: x > (sensor_data.time - FIXED_VAL), self.light_time))

        avg_l = sum(self.light_data[-len(time_filtered):]) / len(time_filtered)
        if self._state.isIndoor:
            if avg_l > SWITCH_2_OUTDOOR_THRESHOLD:
                self._state.setStateNumber(self._state.getStateNumber() & int(0b101))  # toggle to no floor change
                if DEBUG:
                    print('OUDR. Time: {:8d} Average: {:.8f}'.format(
                        sensor_data.time, avg_l))
                print(STR_OUDR % sensor_data.time)
                self.io_last_change = sensor_data.time
            return
        if avg_l < SWITCH_2_INDOOR_THRESHOLD:
            self._state.setStateNumber(self._state.getStateNumber() | int(0b010))  # toggle to no floor change
            if DEBUG:
                print('INDR. Time: {:8d} Average: {:.8f}'.format(
                    sensor_data.time, avg_l))
            print(STR_INDR % sensor_data.time)
            self.io_last_change = sensor_data.time

    def classify_single_data(self, sensor_data):
        self.counter += 1
        if sensor_data._type == 'a':
            cur_a = sensor_data.values
            delta_v = minus(cur_a, self.prev_a)
            delta_sum = sum(map(pow2, delta_v))
            self.prev_a = cur_a
            self.moving_a_delta = self.moving_a_delta * WALK_DIM_FACTOR + delta_sum
            return self.decide_moving_state(sensor_data, delta_sum)

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

            return self.decide_floor_state(sensor_data)

        if sensor_data._type == 'l':
            cur_l = sensor_data.values
            try:
                delta_l = cur_l[0] - self.light_data[-1]
                if delta_l > LIGHT_DAMP_THRESHOLD and self.light_data[-1]:
                    cur_l = [self.light_data[-1] + delta_l * LIGHT_DAMP_FACTOR]
            except IndexError:  # initial entry
                pass
            self.light_data += cur_l
            self.light_time += [sensor_data.time]

            return self.decide_iodoor_state(sensor_data)

        # raise Exception('IDK WHAT TO DO WITH THIS INPUT: ' + sensor_data)
