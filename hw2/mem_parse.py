import sys

fn = sys.argv[1]
with open(fn, 'r') as f:
    d = [0, 0, 0, 0]
    index = 0
    for line in f:
        d[index] = line.strip()
        index += 1
        if index == 4:
            print ",".join(map(str, d))
        index %= 4
