#! /usr/bin/python


import rospy as rp
import geomtwo.msg as gms
import geomtwo.impl as gmi
import std_msgs.msg as sms
import circumnavigation_cloud.srv as ccs


import threading as thd



rp.init_node(name='monitor')

AGENT_NAMES = rp.get_param('agent_names').split()
LOCK = thd.Lock()

bearings = dict()
betas = dict()
for name in AGENT_NAMES:
    bearings[name] = None
    betas[name] = None

cloud_access_beta_pubs = dict()
for name in AGENT_NAMES:
    cloud_access_beta_pubs[name] = rp.Publisher(name="{}/cloud_access_beta".format(name), data_class=sms.Float64, queue_size=10)

def bearing_callback(msg, name):
    LOCK.acquire()
    bearings[name] = gmi.Versor(msg)
    LOCK.release()

def cloud_access_callback(msg, name):
    LOCK.acquire()
    if name in betas: cloud_access_beta_pubs[name].publish(betas[name])
    LOCK.release()

beta_pubs = dict()
for name in AGENT_NAMES:
    rp.Subscriber(name='{}/bearing'.format(name), data_class=gms.Versor, queue_size=10, callback=bearing_callback, callback_args=name)
    beta_pubs[name] = rp.Publisher(name='{}/real_beta'.format(name), data_class=sms.Float64, queue_size=10)



RATE = rp.Rate(5.0)
while not rp.is_shutdown():
    LOCK.acquire()
    for name in AGENT_NAMES:
        if not bearings[name] is None:
            betas[name] = min(( bearings[name].angle_to(bearings[other], force_positive=True) for other in AGENT_NAMES if other != name and not bearings[other] is None ))
    LOCK.release()
    for name in AGENT_NAMES: beta_pubs[name].publish(betas[name])
    RATE.sleep()
