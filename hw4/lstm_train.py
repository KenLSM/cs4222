import argparse
import csv
import sys
import os

import numpy as np

from classifiers.lstm_classifier import LstmClassifier, BATCH_TIME_STEPS

def main(args):
    classifier = LstmClassifier()
    training_features = []
    training_labels = []
    for data_file in args.data_files.split(','):
        if not os.path.exists(data_file):
            print("Could not find data file in %s" % data_file)

        with open(data_file, 'r') as f:
            reader = csv.reader(f, delimiter=',')
            features = []
            labels = []
            data_rows = [np.asarray(x, dtype=np.float32) for x in reader]
            num_examples = len(data_rows)
            offset = (BATCH_TIME_STEPS - num_examples % BATCH_TIME_STEPS) % BATCH_TIME_STEPS
            data_rows.extend([np.zeros((9,), dtype=np.int) for _ in range(0, offset)])
            num_subsequences = len(data_rows) / BATCH_TIME_STEPS
            all_subsequences = np.split(np.stack(data_rows), num_subsequences)
            for subsequence in all_subsequences:
                features.append(subsequence[:,2:9])
                labels.append(subsequence[:,1:2])
            features = np.stack(features)
            labels = np.squeeze(np.stack(labels), 2)
            labels = labels.astype(np.int)
            training_features.append(features)
            training_labels.append(labels)

    classifier.train(training_features, training_labels)
    classifier.save_model(args.model_dir, args.model_basename)


def parse_arguments(argv):
    parser = argparse.ArgumentParser()
    # Data files args
    parser.add_argument('--data_files', type=str,
                        help='Comma delimited strings of data filenames')
    parser.add_argument('--model_dir', type=str,
                        help='Directory of model to be used')
    parser.add_argument('--model_basename', type=str,
                        help='basename for model to use')
    return parser.parse_args(argv)

if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))