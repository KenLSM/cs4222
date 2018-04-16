from classifiers.classes import SensorData
from classifiers.state_machine_classifier import StateMachineClassifier

# input_file = 'walk_1_prepro/data_collect_2018_03_20_13_52_12.csv'
input_file = 'walk_2_prepro/data_collect_2018_03_20_14_08_54.csv'


def parser(input):
    try:
        l = input.split(',')
        if l[1] is 'a':
            d = list(map(float, l[2:5]))
            return SensorData(int(l[0]), l[1], d)
        if l[1] in ['b', 't', 'h', 'l']:
            d = float(l[2])
            return SensorData(int(l[0]), l[1], [d])
        return None
    except Exception:
        return None


# return true if sensor data is of type t
def filter_type(t, sensor_data):
    # print(sensor_data._type)
    return sensor_data._type is t


# return true if sensor data is between time
def filter_time_range(begin, end, sensor_data):
    return sensor_data.time > begin and sensor_data.time < end


def get_type(t, sensor_data_set):
    return list(filter(lambda d: filter_type(t, d), sensor_data_set))


def get_range(begin, end, sensor_data_set):
    return list(filter(lambda d: filter_time_range(begin, end, d), sensor_data_set))


with open(input_file, 'r') as f:
    data_set = f.read().split('\n')
    parsed_set = []
    for d in data_set:
        if parser(d) is not None:
            parsed_set += [parser(d)]

d = get_range(0, 600000, parsed_set)
# d = get_type('l', d)

k_class = StateMachineClassifier()

print(len(d))

for ds in d[::1]:
    k_class.classify([ds])
