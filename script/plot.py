import matplotlib.pyplot as plt
import rosbag as rb
import sys
import math

bagfilename = sys.argv[1]
bag = rb.Bag(bagfilename)

COLORS = iter("blue red green orange magenta cyan purple".split())
lines = dict()
times = list()
start_time = None
sample = None

for topic, msg, time in bag.read_messages(topics=['/agent1/beta', '/agent2/beta', '/agent3/beta']):
    if sample is None:
        sample = topic
        print topic
    if start_time is None:
        start_time = time.to_sec()
    if sample == topic:
        times.append(time.to_sec()-start_time)
    if not topic in lines:
        lines[topic] = {"time":list(), "data":list()}
    lines[topic]["time"].append(time.to_sec()-start_time)
    lines[topic]["data"].append(msg.data)
bag.close()



plt.figure()
plt.grid(True)
for name, line in lines.items():
    plt.plot(line["time"], line["data"], label=r'$\beta_i(t)$', color=next(COLORS))
plt.legend()
plt.xlabel(r"$t$")


plt.show()