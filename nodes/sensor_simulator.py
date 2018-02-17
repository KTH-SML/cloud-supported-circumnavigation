#! /usr/bin/python

import rospy as rp
import geomtwo.msg as gms
import geomtwo.impl as gmi
import threading as thd

import circumnavigation_cloud.srv as ccs






LOCK = thd.Lock()



rp.init_node('sensor_simulator')


def target_position_callback(msg):
    global target_position
    LOCK.acquire()
    target_position = gmi.Point(msg)
    LOCK.release()

rp.Subscriber(
    name = "/target_position",
    data_class = gms.Point,
    callback = target_position_callback,
    queue_size = 10)


def position_callback(msg):
    global position
    LOCK.acquire()
    position = gmi.Point(msg)
    LOCK.release()

rp.Subscriber(
    name='vehicle_position',
    data_class = gms.Vector,
    callback=position_callback,
    queue_size=10)




rp.wait_for_message('vehicle_position', gms.Point)
rp.wait_for_message('/target_position', gms.Point)


#Handler for the service SensorService
def sensor_service_handler(req):
    LOCK.acquire()
    bearing = gmi.Versor(target_position-position)
    LOCK.release()
    return ccs.SensorServiceResponse(bearing.serialize())

rp.Service(
    name = 'sensor_service',
    service_class = ccs.SensorService,
    handler = sensor_service_handler)


rp.spin()
