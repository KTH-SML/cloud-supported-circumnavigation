#!/usr/bin/python

import rospy as rp
import geomtwo.msg as gms
import geomtwo.impl as gmi
import std_msgs.msg as smsp
import circumnavigation_cloud.srv as ccs


import threading as thd



GAIN = rp.get_param('/gain')
ALPHA = rp.get_param('/alpha')


rp.init_node('cloud')
# AGENT_NAMES = rp.get_param('agent_names').split()

access_times = dict()
bearings = dict()
control_values = dict()
scheduled_accesses = dict()



LOCK=thd.Lock()



def cloud_handler(req):
    time = rp.get_time()
    LOCK.acquire()
    access_times[req.name] = time
    bearings[req.name] = gmi.Versor(req.bearing)
    current_bearings = dict()
    for name in access_times:
        if name != req.name: current_bearings[name] = bearings[name].rotate(control_values[name]*(time-access_times[name]))
    if len(current_bearings) > 0:
        beta = min( ( bearings[req.name].angle_to( current_bearing, force_positive=True ) for current_bearing in current_bearings.values() ) )
        control_values[req.name] = GAIN*(ALPHA+beta)
        next_access = time + beta/control_values[req.name]
    else:
        beta = 0.0
        control_values[req.name] = GAIN*(ALPHA+beta)
        next_access = time + 1.0
    scheduled_accesses[req.name] = next_access
    LOCK.release()
    return ccs.CloudServiceResponse(beta, next_access)


rp.Service('cloud_service', ccs.CloudService, cloud_handler)
rp.loginfo('Cloud service started')

rp.spin()
