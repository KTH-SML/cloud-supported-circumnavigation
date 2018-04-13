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
sample = None


for topic, msg, time in bag.read_messages(topics=['/clara/cloud_access', '/dario/cloud_access', '/antonio/cloud_access', '/francesco/cloud_access', '/davide/cloud_access']):
    if sample is None:
        sample = topic
        print topic
    if start_time is None:
        start_time = time.to_sec()
    if sample == topic:
        times.append(time.to_sec()-start_time)
    if not topic in lines:
        lines[topic] = list()
    lines[topic].append(time.to_sec()-start_time)
bag.close()



plt.figure()
plt.grid(True)
for index, tup in enumerate(lines.items()):
    name, line = tup
    plt.scatter(line, [index]*len(line), label=name, color=next(COLORS))
    plt.xlim([0,max(line)])
# plt.legend()
plt.xlabel(r"$t$")
plt.ylabel(r'$i$')
plt.savefig("./pics/accesses.pdf")


plt.show()
