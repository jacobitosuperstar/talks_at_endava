"""Following the log files??
"""

import os
import time


def follow(filename):
    f =  open(filename, "r")
    f.seek(0, os.SEEK_END)

    while True:
        line = f.readline()
        if not line:
            time.sleep(0.0001)
            continue
        # print("Got: ", line)
        yield line

for line in follow("log.log"):
    if "**" in line:
        print(line)
