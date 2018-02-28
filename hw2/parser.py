"""
Input file assumed to be"
-1.20 G, 0.24 G, -0.21 G
-1.23 G, 0.24 G, -0.21 G
...
...
-1.25 G, 0.24 G, -0.22 G
-1.28 G, 0.24 G, -0.22 G
"""

GRAV = 9.81

file = "data/processed_data/sample3.csv"

data = []
with open(file, "r") as input_file:
    for line in input_file:
        line = line.strip()
        if line is "":
            continue
        if line[0] is not "#":
            # split by "," then reverse arrangement to x, y, z axis
            d = line.split(",")[::-1]
            # remove last char which is "G" and convert to ms2 and round to 2dp
            data += [map(lambda x: round(float(x.strip()[:-1]) * GRAV, 2), d)]


processed_file = file + "_p"

with open(processed_file, "w") as write_file:
    for line in data:
        write_file.write((",".join(map(str, line)) + "\n"))
