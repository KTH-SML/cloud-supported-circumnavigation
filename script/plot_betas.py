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


for topic, msg, time in bag.read_messages(topics=['/clara/real_beta', '/dario/real_beta', '/antonio/real_beta', '/francesco/real_beta', '/davide/real_beta']):
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
    plt.plot(line["time"], line["data"], label=name, color=next(COLORS), linewidth=2)
    plt.xlim([0, max(line["time"])])
# plt.legend()
plt.xlabel(r"$t$")
plt.ylabel(r'$\beta_i(t)$')
plt.savefig("./pics/betas.pdf")

plt.show()
