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


GAIN = rp.get_param('/gain')
ALPHA = rp.get_param('/alpha')
DESIRED_DISTANCE = rp.get_param('/desired_distance')
NAME = rp.get_param('name')

LOCK = thd.Lock()


vehicle_position = None
measured_bearing = None
estimated_bearing = None

received_beta = 0.0
next_cloud_access = 0.0


rp.init_node('controller')
RATE = rp.Rate(60.0)






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


rp.wait_for_service('/cloud_service')
cloud_service_proxy = rp.ServiceProxy('/cloud_service', ccs.CloudService)




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
    if rp.get_time() > next_cloud_access:
        rp.loginfo('{} is accessing the cloud'.format(NAME))
        response = cloud_service_proxy.call(NAME, estimated_bearing)
        received_beta = response.beta
        next_cloud_access = response.next_access
    tangent_versor = estimated_bearing.rotate(-mth.pi/2)
    cmdvel = GAIN*(ALPHA+received_beta)*tangent_versor
    LOCK.release()

    cmdvel_pub.publish(cmdvel.serialize())
    estimate_publisher.publish(estimated_target_position.serialize())

    RATE.sleep()
