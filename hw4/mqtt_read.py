import os
import re
import threading
from itertools import groupby
from threading import Semaphore
import paho.mqtt.client as mqtt

from classifiers.classes import SensorData
from classifiers.state_machine_classifier import StateMachineClassifier

SENSOR_OUTPUT_FILENAME = 'output.csv'

MAX_BUFFER_WINDOW = 100
data_buffer = []
data_semaphore = Semaphore(1)
classifier = StateMachineClassifier()
refresh_timer = None

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


def parse_payload(payload_str):
    re_pattern = ".*unicast message received from 77.2,(.+?)\".*"
    m = re.search(re_pattern, payload_str)
    if not m:
        return None
    return parser(m.group(1))


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("#")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global refresh_timer
    payload = msg.payload.decode("utf-8")
    sensor_data = parse_payload(payload)
    data_semaphore.acquire()
    data_buffer.append(sensor_data)
    if len(data_buffer) >= MAX_BUFFER_WINDOW:
        process_data(data_buffer[:])
        data_buffer[:] = []
    data_semaphore.release()
    if refresh_timer is not None:
        refresh_timer.cancel()
    refresh_timer = threading.Timer(10, on_refresh)
    refresh_timer.start()


def process_data(sensor_datas):
    # Sort and pass into classifier a list of sensor data for each time step
    sensor_datas = sorted(sensor_datas, key=lambda sensor_data: sensor_data.time)
    with open(SENSOR_OUTPUT_FILENAME, 'a') as f:
        for sensor_data in sensor_datas:
            f.write("%s\n" % str(sensor_data))

    for time, group in groupby(sensor_datas, key=lambda sensor_data: sensor_data.time):
        state = classifier.classify(list(group))  # state_machine doesn't return
        # print("%d" % time) # Make use of new state here (only print if changed etc)


# Periodic callback to refresh data buffer
def on_refresh():
    data_semaphore.acquire()
    if len(data_buffer) is not 0:
        process_data(data_buffer[:])
        data_buffer[:] = []
    data_semaphore.release()

if os.path.exists(SENSOR_OUTPUT_FILENAME):
    os.remove(SENSOR_OUTPUT_FILENAME)

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
