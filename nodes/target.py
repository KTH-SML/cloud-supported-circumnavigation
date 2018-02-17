#!/usr/bin/python

import rospy as rp
import geomtwo.msg as gms
import geomtwo.impl as gmi
import threading as thd
import numpy as np
import circumnavigation_cloud.srv as srvc


TARGET_POSITION = gmi.Point(0.0,0.0)

publisher = rp.Publisher(
    name = "target_position",
    data_class = gms.Point,
    queue_size = 10)

rp.init_node("target")
RATE = rp.Rate(30.0)
while not rp.is_shutdown():
    publisher.publish(TARGET_POSITION.serialize())
    RATE.sleep()
