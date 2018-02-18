#!/usr/bin/python


import rospy as rp
import geomtwo.msg as gms
import geomtwo.impl as gmi
import std_msgs.msg as sms

import threading as thd


rp.init_node('vehicle_simulator')

LOCK = thd.Lock()

position = gmi.Point(rp.get_param("initial_position"))
position_timestamp = rp.get_time()
velocity = gmi.Vector()



FREQUENCY = 60.0
RATE = rp.Rate(FREQUENCY)
TIME_STEP = 1.0/FREQUENCY

def cmdvel_callback(msg):
    global velocity
    LOCK.acquire()
    velocity = gmi.Vector(msg)
    LOCK.release()

rp.Subscriber(
    name = 'cmdvel',
    data_class = gms.Vector,
    callback = cmdvel_callback,
    queue_size = 10)


#Publisher
pub = rp.Publisher(
    name='vehicle_position',
    data_class=gms.Point,
    queue_size=10)





while not rp.is_shutdown():
    LOCK.acquire()
    time = rp.get_time()
    position += (time-position_timestamp)*velocity
    position_timestamp = time
    # velocity = gmi.Vector()
    LOCK.release()
    pub.publish(position.serialize())
    RATE.sleep()
