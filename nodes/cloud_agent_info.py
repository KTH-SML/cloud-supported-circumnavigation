#!/usr/bin/python

import rospy as rp
import geomtwo.msg as gms
import geomtwo.impl as gmi
import std_msgs.msg as smsp
import circumnavigation_cloud.srv as srvc


import threading as thd
import numpy as np
import math




rp.init_node('cloud_agent_info')
AGENT_NAMES = rp.get_param('agent_names').split()
access_times = dict()
bearing_measurements = dict()
control_values = dict()




LOCK=thd.Lock()



def cloud_handler(req):
    LOCK.acquire()
    # rp.logwarn('Cloud service hb')
    time = rp.get_time()
    access_times[req.ID] = time
    bearing_measurements[req.ID] = gmi.Versor(req.bearing_measurement)
    current_bearings = dict()
    for name in AGENT_NAMES:
        if name != req.ID and name in access_times:
            current_bearings[name] = bearing_measurements[name].rotate(control_values[name]*(time-access_times[name]))
    if len(current_bearings) > 0:
        beta = min((bearing_measurements[req.ID].angle_to(current_bearing, force_positive=True) for current_bearing in current_bearings.values()))
    else: beta = 0.0
    control_values[req.ID] = beta
    LOCK.release()
    return srvc.CloudServiceResponse(beta)


rp.Service('Cloud_Service', srvc.CloudService, cloud_handler)
rp.logwarn('Cloud service started')

rp.spin()
