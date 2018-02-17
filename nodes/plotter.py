#! /usr/bin/python


import matplotlib as mpl
import numpy as np
import threading as thd
import copy as cp
import matplotlib.pyplot as plt

import rospy as rp
import geomtwo.msg as gms
import geomtwo.impl as gmi
import std_msgs.msg as smsp




rp.init_node('plotter')

RATE = rp.Rate(30.0)

TARGET_COLOR = "red"

AGENT_NAMES = rp.get_param('agent_names').split()
AGENT_COLORS = {name: color for (name,color) in zip (AGENT_NAMES, rp.get_param('agent_colors').split()) }
# TARGET_POSITION = rp.get_param('target_position')



LOCK = thd.Lock()


plt.ion()
plt.figure()
# plt.scatter(*TARGET_POSITION, color=TARGET_COLOR)
# circle=plt.Circle(TARGET_POSITION, 1.0, color='r', fill=False, linestyle='dashed')
# ax = plt.gca()
# ax.add_patch(circle)
plt.axis("equal")
plt.xlim([-5,5])
plt.ylim([-5,5])
plt.grid(True)
plt.draw()

agent_positions = {name: None for name in AGENT_NAMES}
agent_artists = {name: None for name in AGENT_NAMES}

estimate_positions = {name: None for name in AGENT_NAMES}
estimate_artists = {name: None for name in AGENT_NAMES}



def agent_callback(msg,name):
    global agent_positions
    LOCK.acquire()
    agent_positions[name] =  gmi.Point(msg)
    LOCK.release()

for name in AGENT_NAMES:
    rp.Subscriber(
        name = name+'/vehicle_position',
        data_class = gms.Point,
        callback = agent_callback,
        callback_args = name,
        queue_size = 10)


def estimate_callback(msg,name):
    global estimate_positions
    LOCK.acquire()
    estimate_positions[name] =  gmi.Point(msg)
    LOCK.release()

for name in AGENT_NAMES:
    rp.Subscriber(
        name = name+'/estimated_target_position',
        data_class = gms.Point,
        callback = estimate_callback,
        callback_args = name,
        queue_size = 10)


target_position = None
target_artists = None

def target_callback(msg):
    global target_position
    LOCK.acquire()
    target_position = gmi.Point(msg)
    LOCK.release()

rp.Subscriber(
    name = "target_position",
    data_class = gms.Point,
    callback = target_callback,
    queue_size = 10)




while not rp.is_shutdown():
    LOCK.acquire()
    if not target_artists is None:
        for artist in target_artists: artist.remove()
    if not target_position is None:
        target_artists = target_position.draw(s=50, facecolor=TARGET_COLOR, edgecolor="black")
    for name in AGENT_NAMES:
        if not agent_artists[name] is None:
            for artist in agent_artists[name]: artist.remove()
        if not agent_positions[name] is None: agent_artists[name] = agent_positions[name].draw(s=50, facecolor=AGENT_COLORS[name], edgecolor="black")
        if not estimate_artists[name] is None:
            for artist in estimate_artists[name]: artist.remove()
        if not estimate_positions[name] is None: estimate_artists[name] = estimate_positions[name].draw(s=50, color=AGENT_COLORS[name], marker="x")
    LOCK.release()
    plt.draw()
    RATE.sleep()

# rp.logwarn('Plotting started')
# while not rp.is_shutdown():
#     ag_pos = {name: None for name in AGENT_NAMES}
#     LOCK.acquire()
#     for name in AGENT_NAMES:
#         if not agent_positions[name] is None:
#             ag_pos[name] = cp.copy(agent_positions[name])
#             agent_positions[name] = None
#     LOCK.release()
#     for name in AGENT_NAMES:
#         if not ag_pos[name] is None:
#             if not agent_artists[name] is None:
#                 for artist in agent_artists[name]: artist.remove()
#             agent_artists[name] = ag_pos[name].draw(color=AGENT_COLOR)
#     plt.draw()
#     # rp.logwarn('Plotter hearthbeat')
#     RATE.sleep()
