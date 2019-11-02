#!/usr/bin/env python

import rospy
from std_msgs.msg import String
from rospy_tutorials.msg import Floats
from rospy.numpy_msg import numpy_msg

def callback(data):
    # print rospy.get_name(), "I heard %s"%str(data.data)
    rospy.loginfo(rospy.get_caller_id() + "I heard FLOAT %s"%str(data.data))

def callbackS(data):
 rospy.loginfo(rospy.get_caller_id() + "I heard string %s", data.data)

def listener():
    rospy.init_node('listener')
    rospy.Subscriber("floats", numpy_msg(Floats), callback)
    rospy.Subscriber("chatter", String, callbackS)
    rospy.spin()

if __name__ == '__main__':
    listener()
