from .classifier import Classifier
from .classes import State
import operator


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
DIM_FACTOR = 0.95  # at 50th element, it will take 7.6% of its original value
SWITCH_2_WALK_THRESHOLD = 0.3
SWITCH_2_IDLE_THRESHOLD = 0.1


class StateMachineClassifier(Classifier):
    prev_a = None
    moving_a_delta = None
    _state = None

    def __init__(self, window_size=1000):
        self.prev_a = []
        self.moving_a_delta = .0
        self._state = State()
        self.counter = 0
        pass

    def decide_moving_state(self, sensor_data, delta_sum):
        if self._state.isWalking:
            if self.moving_a_delta < SWITCH_2_IDLE_THRESHOLD:
                self._state.setStateNumber(self._state.getStateNumber() & int(0b110))  # toggle to idle
                print('SLOW. Time: {:8d} Avg: {:.6} Sum: {:.6}'.format(
                    sensor_data.time, self.moving_a_delta, delta_sum))
                print(self._state.getStateNumber())
            return
        if self.moving_a_delta > SWITCH_2_WALK_THRESHOLD:
            self._state.setStateNumber(self._state.getStateNumber() | int(0b001))  # toggle to walking
            print('FAST. Time: {:8d} Avg: {:.6} Sum: {:.6}'.format(
                sensor_data.time, self.moving_a_delta, delta_sum))
            print(self._state.getStateNumber())

    def classify(self, sensor_data):
        self.counter += 1
        if sensor_data._type == 'a':
            cur_a = sensor_data.values
            delta_v = minus(cur_a, self.prev_a)
            delta_sum = sum(map(pow2, delta_v))
            self.prev_a = cur_a
            self.moving_a_delta = self.moving_a_delta * DIM_FACTOR + delta_sum
            # if self.counter % 500 is 1:
            #     print('Time: {:8d} Avg: {:.6} Cur: {:.6f}'.format(
            #         sensor_data.time, self.moving_a_delta, delta_sum))
            self.decide_moving_state(sensor_data, delta_sum)

            return
        raise Exception('IDK WHAT TO DO WITH THIS INPUT: ' + sensor_data)
