import argparse
import csv
import os
import io

import sys
from itertools import groupby

from classifiers.classes import State


def main(args):
    if not os.path.exists(args.data_file):
        print("Could not find data file in %s" % args.data_file)
    if not os.path.exists(args.activities_file):
        print("Could not find activities file in %s" % args.activities_file)

    with io.open(args.activities_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f, delimiter=',')
        activities = list(reader) # list of tuples (time, activity)
        activities = {time: activity for time, activity in activities}

    with open(args.data_file, 'r') as f:
        reader = csv.reader(f, delimiter=',')
        grouped_by_time = groupby(reader, key=lambda row: row[0])
        grouped_by_time = [(time, list(group)) for time, group in grouped_by_time]

    with open(args.out_file, 'w', newline="") as f:
        writer = csv.writer(f, delimiter=',')
        last_state = State()
        for time, group in grouped_by_time:
            if time in activities:
                activity = activities[time]
                setActivity(last_state, activity)
            out_row = [time, last_state.getStateNumber(), 0, 0, 0, 0, 0, 0, 0]
            for sensor_data in group:
                if sensor_data[1] == 'a':
                    out_row[2:5] = sensor_data[2:5]
                elif sensor_data[1] == 'b':
                    out_row[5:6] = sensor_data[2:3]
                elif sensor_data[1] == 't':
                    out_row[6:7] = sensor_data[2:3]
                elif sensor_data[1] == 'l':
                    out_row[7:8] = sensor_data[2:3]
                elif sensor_data[1] == 'h':
                    out_row[8:9] = sensor_data[2:3]
                else:
                    raise Exception("Something went wrong")
            writer.writerow(out_row)

def setActivity(state, activity_name):
    if activity_name == 'WALKING':
        state.isWalking = True
    elif activity_name == 'IDLE':
        state.isWalking = False
    elif activity_name == 'FLOORCHANGE':
        state.isFloorChange = True
    elif activity_name == 'NOFLOORCHANGE':
        state.isFloorChange = False
    elif activity_name == 'INDOOR':
        state.isIndoor = True
    elif activity_name == 'OUTDOOR':
        state.isIndoor = False

def parse_arguments(argv):
    parser = argparse.ArgumentParser()
    # Data files args
    parser.add_argument('--data_file', type=str,
                        help='CSV file containing data')
    parser.add_argument('--activities_file', type=str,
                        help='CSV file containing activities')
    parser.add_argument('--out_file', type=str,
                        help='CSV file for output data')
    return parser.parse_args(argv)


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))