import os
import random

import numpy as np
from keras.layers import LSTM, Dense
from keras.models import load_model, Sequential
from keras.optimizers import adam
from keras.utils import to_categorical

from classifiers.classes import State
from classifiers.classifier import Classifier

EXTENSION_H5 = '.h5'
BATCH_TIME_STEPS = 128
NUM_FEATURES = 7

class LstmClassifier(Classifier):

    model = None

    def __init__(self, model_dir=None, model_basename=None):
        """ Classifies based on a list of sensor data for 1 time step
            and uses the current state of classifier to return a prediction.
            Returns a state as defined in state class.
         """
        if model_dir is not None and model_basename is not None:
            self.load_model(model_dir, model_basename)
        else:
            self.new_model()

    def classify(self, sensor_datas):
        """ Classifies based on a list of sensor data for 1 time step
            and uses the current state of classifier to return a prediction.
            Returns a state as defined in state class.
         """
        features = [0 for _ in range(0, 7)]
        state = State()
        for sensor_data in sensor_datas:
            if sensor_data.type == 'a':
                features[0:3] = sensor_data.values
            elif sensor_data.type == 'b':
                features[3:4] = sensor_data.values
            elif sensor_data.type == 't':
                features[4:5] = sensor_data.values
            elif sensor_data.type == 'l':
                features[5:6] = sensor_data.values
            elif sensor_data.type == 'h':
                features[6:7] = sensor_data.values
        features = np.expand_dims(features, 0)
        prediction = self.predict(features)
        state.setStateNumber(prediction[0])
        return state

    def predict(self, input):
        """ Takes in as input features of shape (BATCH_TIME_STEPS, NUM_FEATURES)
            Returns an array of predicted class indices in shape of (BATCH_TIME_STEPS)
        """
        output = np.expand_dims(input, 0)
        output = self.model.predict(output, 1)
        output = np.squeeze(output, 0)
        output = np.argmax(output, 1)
        return output

    def train(self, data, labels):
        """
        :param data: List of batches of full time series of feature values at each time step.
            Shape of (BATCH_SIZE, NUMBER_OF_SUBSEQUENCES, BATCH_TIME_STEPS, 7)
        :param labels: List of labels for each corresponding batch
            Shape of (BATCH_SIZE, NUMBER_OF_SUBSEQUENCES, BATCH_TIME_STEPS,)
        :return:
        """
        all_class_weights = [None for _ in range(len(data))]
        for epoch in range(0, 40):
            print("Epoch: %d" % epoch)
            for idx, batch_data in enumerate(data):
                self.model.reset_states()
                if all_class_weights[idx] is None:
                    all_class_weights[idx] = self.get_class_weights(labels[idx])
                print("Training on batch %d" % idx)
                for sub_idx, subsequence_data in enumerate(batch_data):
                    # if random.uniform(0, 1) > 0.7:
                    #     continue
                    subsequence_data = np.expand_dims(subsequence_data, 0)
                    subsequence_labels = to_categorical(labels[idx][sub_idx], num_classes=8)
                    subsequence_labels = np.expand_dims(subsequence_labels, 0)
                    self.model.fit(x=subsequence_data,
                                   y=subsequence_labels,
                                   class_weight=all_class_weights[idx],
                                   batch_size=1, epochs=1, verbose=0, shuffle=False)
            self.evaluate(data, labels)

    def get_class_weights(self, labels):
        bin_count = np.bincount(labels.flatten()) + 10
        median_count = np.median(bin_count).item(0)
        class_weights = np.full_like(bin_count, median_count) / bin_count
        return class_weights

    def evaluate(self, eval_features, eval_labels):
        num_examples = 0
        correct = 0
        for idx, batch_eval_features in enumerate(eval_features):
            self.model.reset_states()
            batch_eval_labels = eval_labels[idx]
            num_examples += np.size(batch_eval_labels)
            for idx, feature in enumerate(batch_eval_features):
                if idx >= num_examples:
                    break
                label = batch_eval_labels[idx]
                result = self.predict(feature)
                correct += np.sum(result == label)
        print(correct / num_examples)

    def new_model(self):
        self.model = Sequential()
        self.model.add(LSTM(units=128, return_sequences=True,
                            batch_input_shape=(1, None, NUM_FEATURES),
                            stateful=True))
        self.model.add(Dense(units=8, activation="softmax"))
        self.model.compile(optimizer=adam(lr=0.01),
                           loss="categorical_crossentropy")

    def save_model(self, model_dir, model_basename):
        """
        Saves trained sklearn model.
        Saves in pickle and coreml formats.
        :param model_dir Directory to be used for saving models.
        :param model_basename Base name of output model. File extension
            is appended to this basename in the overall filename.
        """
        if self.model is None:
            raise Exception("Classifier model is not created yet")
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)

        # Save to keras model file
        keras_model_path = os.path.join(
            model_dir, model_basename + EXTENSION_H5)
        self.model.save(keras_model_path)

    def load_model(self, model_dir, model_basename):
        """
        Loads model into object
        :param model_path: file name for model to be loaded.
        """
        keras_model_path = os.path.join(
            model_dir, model_basename + EXTENSION_H5)
        self.model = load_model(keras_model_path)
