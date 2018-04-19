from itertools import groupby
from threading import Semaphore
import paho.mqtt.client as mqtt

# from classifiers.classifier import Classifier
from classifiers.state_machine_classifier import StateMachineClassifier

MAX_BUFFER_WINDOW = 100
data_buffer = []
data_semaphore = Semaphore(1)
# classifier = Classifier() # need to use a implemented one
classifier = StateMachineClassifier()


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("#")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))
    data_semaphore.acquire()
    data_buffer.append(msg.payload)  # Need to parse msg and pass in SensorData object here
    if len(data_buffer) >= MAX_BUFFER_WINDOW:
        process_data(data_buffer[:])
        data_buffer[:] = []
    data_semaphore.release()


def process_data(sensor_datas):
    # Sort and pass into classifier a list of sensor data for each time step
    sensor_datas = sorted(sensor_datas, key=lambda sensor_data: sensor_data.time)
    for time, group in groupby(sensor_datas, key=lambda sensor_data: sensor_data.time):
        state = classifier.classify(list(group))  # state_machine doesn't return
        # print("%d" % time) # Make use of new state here (only print if changed etc)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.username_pw_set("cs4222group22@gmail.com", "NpGzXLKuFhQVfekJ")

client.connect("ocean.comp.nus.edu.sg")

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
