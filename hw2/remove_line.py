import sys

f = sys.argv[1]

with open(f, 'r') as csv:
    i = 10
    for line in csv:
        i *= -1
        if i < 0:
            print line,
