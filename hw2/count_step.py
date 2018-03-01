import math
import sys

DEBUG = False

half_window_size = 15  # the actual window size will be (half_window_size * 2 + 1)
T1 = 2
T2 = 1
if len(sys.argv) < 2:
    raise Exception("Please provide an input file as a cmd line argument.")


input_arr = []


def get_mag(d):
    return math.sqrt(sum(map(lambda x: x**2, d)))


if DEBUG:
    print(get_mag([1, 2, 3]))


file_name = sys.argv[1]
with open(file_name, "r") as f:
    for line in f:
        if DEBUG:
            print(line)
        mag = get_mag(map(float, line.split(",")))
        input_arr += [mag]


input_length = len(input_arr)

if DEBUG:
    print(input_arr)
    print("Received input length of", input_length)

var_arr = []
for i in range(input_length):
    left_win = max(0, i - half_window_size)
    right_win = min(input_length - 1, i + half_window_size)

    N = right_win - left_win
    if DEBUG:
        print(N)

    mean = sum(input_arr[left_win:right_win]) / N
    x_2_sum = 0
    for j in range(left_win, right_win + 1):
        x_2_sum += (input_arr[j] - mean) ** 2
    var_arr += [x_2_sum / N]


if DEBUG:
    print(var_arr)

t1_eval = []
for i in var_arr:
    t1_eval += [T1 if i < T1 else 0]

if DEBUG:
    print(t1_eval)

prev = 0
count = 0
for i in t1_eval:
    if i is 0 and prev is T1:
        count += 1
    prev = i

print(count)
