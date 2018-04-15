import argparse
import csv
import sys
import os
import io


def main(args):
    if not os.path.exists(args.data_file):
        print("Could not find data file in %s" % args.data_file)

    with io.open(args.activities_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f, delimiter=',')
        activities = list(reader) # list of tuples (time, activity)

    out_rows = []
    with open(args.data_file, 'r') as f:
        last_ptr = 0
        next_activity_ptr = 1
        reader = csv.reader(f, delimiter=',')
        activity_times = [float(time) for time, _ in activities]
        activity_times.append(9999999999)
        for idx, row in enumerate(reader):
            row = [float(x) for x in row]
            if idx == 0:
                activity_times = [row[0]] + activity_times
            if next_activity_ptr < len(activity_times) and activity_times[next_activity_ptr] - row[0] >= 1000 and row[0] - activity_times[last_ptr] >= 1000:
                continue
            out_rows.append(row)
            if next_activity_ptr < len(activity_times) and row[0] >= activity_times[next_activity_ptr]:
                next_activity_ptr += 1
                last_ptr += 1

    with open(args.out_file, 'w', newline="") as f:
        writer = csv.writer(f, delimiter=',')
        for row in out_rows:
            writer.writerow(row)


def parse_arguments(argv):
    parser = argparse.ArgumentParser()
    # Data files args
    parser.add_argument('--data_file', type=str,
                        help='CSV File for data to be evaluated')
    parser.add_argument('--activities_file', type=str,
                        help='CSV File for activities')
    parser.add_argument('--out_file', type=str,
                        help='Name of output file')
    return parser.parse_args(argv)

if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))