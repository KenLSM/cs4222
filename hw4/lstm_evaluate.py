import argparse
import csv
import os

import sys

from classifiers.classes import SensorData, State
from classifiers.lstm_classifier import LstmClassifier


def main(args):
    classifier = LstmClassifier(args.model_dir, args.model_basename)
    if not os.path.exists(args.data_file):
        print("Could not find data file in %s" % args.data_file)

    with open(args.data_file, 'r') as f:
        reader = csv.reader(f, delimiter=',')
        last_state = State()
        for row in reader:
            row = [float(x) for x in row]
            sensor_datas = [
                SensorData(row[0], 'a', row[2:5]),
                SensorData(row[0], 'b', row[5:6]),
                SensorData(row[0], 't', row[6:7]),
                SensorData(row[0], 'l', row[7:8]),
                SensorData(row[0], 'h', row[8:9])]
            state = classifier.classify(sensor_datas)
            if state.getStateNumber() != last_state.getStateNumber():
                last_state = state
                print("Time: %s, FloorChange: %s, Indoor: %s, Walking: %s"
                      % (row[0], state.isFloorChange, state.isIndoor, state.isWalking))


def parse_arguments(argv):
    parser = argparse.ArgumentParser()
    # Data files args
    parser.add_argument('--data_file', type=str,
                        help='CSV File for data to be evaluated')
    parser.add_argument('--model_dir', type=str,
                        help='Directory of model to be used')
    parser.add_argument('--model_basename', type=str,
                        help='basename for model to use')
    return parser.parse_args(argv)

if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))