#!/usr/bin/env python

import rospy
import numpy
from std_msgs.msg import String
from rospy.numpy_msg import numpy_msg
from rospy_tutorials.msg import Floats

def talker():
    topic = 'floats'
    pub = rospy.Publisher(topic, numpy_msg(Floats))
    rospy.init_node(topic, anonymous=True)
    r = rospy.Rate(1) # 1hz
    rospy.loginfo("I will publish to the topic %s", topic)
    while not rospy.is_shutdown():
        a = numpy.array([1.0, 2.1, 3.2, 4.3, 5.4, 6.5], dtype=numpy.float32)
	rospy.loginfo(a)
        pub.publish(a)
        r.sleep()
 
if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass
