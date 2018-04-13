import kthcolors.inplace as kti
import matplotlib.pyplot as plt
import rosbag as rb
import sys
import math

bagfilename = sys.argv[1]
bag = rb.Bag(bagfilename)

COLORS = iter("blue green yellow magenta red".split())
lines = dict()
times = list()
start_time = None


for topic, msg, time in bag.read_messages(topics=['/clara/vehicle_position', '/dario/vehicle_position', '/antonio/vehicle_position', '/francesco/vehicle_position', '/davide/vehicle_position']):
    if start_time is None:
        start_time = time.to_sec()
    if not topic in lines:
        lines[topic] = {"time":list(), "x":list(), "y":list()}
    lines[topic]["time"].append(time.to_sec()-start_time)
    lines[topic]["x"].append(msg.x)
    lines[topic]["y"].append(msg.y)
bag.close()



plt.figure()
plt.grid(True)
for name, line in lines.items():
    plt.plot(line["x"], line["y"], label=name, color=next(COLORS))
plt.axis("equal")
# plt.legend()
plt.xlabel(r"$y^{(1)}$")
plt.ylabel(r'$y^{(2)}$')
plt.savefig("./pics/positions.pdf")

plt.show()
