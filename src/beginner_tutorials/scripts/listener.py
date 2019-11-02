#!/usr/bin/env python
import rospy
from std_msgs.msg import String
from rospy.numpy_msg import numpy_msg
from rospy_tutorials.msg import Floats

def callback(data):
 rospy.logwinforospy.get_caller_id() + "I heard %s", data.data)

def callbackF(data):
 rospy.loginfo(rospy.get_caller_id() + "I heard a numpy array %s" %str(data.data))
 #rospy.loginfo(rospy.get_caller_id() + "I heard a numpy array %s"%str(data.data))
 
def listener():

 # In ROS, nodes are uniquely named. If two nodes with the same
 # name are launched, the previous one is kicked off. The
 # anonymous=True flag means that rospy will choose a unique
 # name for our 'listener' node so that multiple listeners can
 # run simultaneously.
 rospy.init_node('listener', anonymous=True)

 rospy.Subscriber("chatter", String, callback)

 rospy.Subscriber("floats", numpy_msg(Floats), callbackF)

 # spin() simply keeps python from exiting until this node is stopped
 rospy.spin()

if __name__ == '__main__':
 listener()
