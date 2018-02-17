#! /usr/bin/python

import sys
sys.ps1 = 'SOMETHING'

import rospy as rp
import geomtwo.msg as gms
import geomtwo.impl as gmi
import std_msgs.msg as sms
import circumnavigation_cloud.srv as ccs

import threading as thd
import math as mth


GAIN = 1.0
ALPHA = 1.0
DESIRED_DISTANCE = 1.0

LOCK = thd.Lock()


vehicle_position = None
measured_bearing = None
estimated_bearing = None


rp.init_node('controller')
RATE = rp.Rate(30.0)






def position_callback(msg):
    global vehicle_position
    LOCK.acquire()
    vehicle_position = gmi.Point(msg)
    LOCK.release()

rp.Subscriber(
    name = 'vehicle_position',
    data_class = gms.Point,
    callback = position_callback,
    queue_size = 10)

rp.wait_for_service('sensor_service')
sensor_proxy = rp.ServiceProxy('sensor_service', ccs.SensorService)
measured_bearing = sensor_proxy.call().bearing_measurement
estimated_bearing = gmi.Versor(measured_bearing)

rp.wait_for_message('vehicle_position', gms.Point)
estimated_target_position = vehicle_position + DESIRED_DISTANCE*estimated_bearing

#Call to the service '/Cloud_Service'
# rp.wait_for_service('/Cloud_Service')
# cloud_proxy = rp.ServiceProxy('/Cloud_Service', srvc.CloudService)
# cloud_resp = cloud_proxy(str(AGENT_NAME), position)
# beta = cloud_resp.beta
# bearing_reference = gmi.Versor(position)




#Publisher
cmdvel_pub = rp.Publisher(
    name = 'cmdvel',
    data_class = gms.Vector,
    queue_size = 10)

estimate_publisher = rp.Publisher(
    name = 'estimated_target_position',
    data_class = gms.Point,
    queue_size = 10)


#Publisher 'beta' (for bagfile)
# beta_pub = rp.Publisher(
#     name='beta',
#     #data_class=gm.ff,
#     data_class=sms.Float64,
#     queue_size=10)



while not rp.is_shutdown():

    LOCK.acquire()
    if estimated_bearing.dot(measured_bearing) < 0.0:
        measured_bearing = sensor_proxy.call().bearing_measurement
        estimated_bearing = gmi.Versor(measured_bearing)
        estimated_target_position = vehicle_position + DESIRED_DISTANCE*estimated_bearing
    else:
        estimated_bearing = gmi.Versor(estimated_target_position - vehicle_position)
    tangent_versor = estimated_bearing.rotate(-mth.pi/2)
    cmdvel = GAIN*ALPHA*tangent_versor
    LOCK.release()

    cmdvel_pub.publish(cmdvel.serialize())
    estimate_publisher.publish(estimated_target_position.serialize())

    RATE.sleep()
