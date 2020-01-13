#!/usr/bin/env python

import rospy
import numpy as numpy
from nav_msgs.msg import Odometry 
from geometry_msgs.msg import Point, Pose, Quaternion, Twist, Vector3
import tf
import sys

gps_coord_x = None
gps_coord_y = None

def callback(odomgps):
    global gps_coord_x, gps_coord_y
    x_offset=225948.249
    y_offset=123119.823
    gps_coord_x=odomgps.pose.pose.position.x+x_offset
    gps_coord_y=odomgps.pose.pose.position.y+y_offset
       
        
def main(args):
    rospy.init_node('gps_odom_covnerter', anonymous=False)
   
    new_gps_pub=rospy.Publisher("odometry/gps/changed", Odometry, queue_size=10)
    gps_sub=rospy.Subscriber("odometry/gps", Odometry, callback)

    gps_coord_x, gps_coord_y

    current_time = rospy.Time.now()
    last_time = rospy.Time.now() 


    rate = rospy.Rate(10)
    while not rospy.is_shutdown():

        odom_quat = tf.transformations.quaternion_from_euler(0, 0, 0)

        odom = Odometry()
        odom.header.stamp = current_time
        odom.header.frame_id = "map"

        # set the position
        odom.pose.pose = Pose(Point(gps_coord_x, gps_coord_y, 0), Quaternion(*odom_quat))

        # set the velocity
        odom.child_frame_id = "base_footprint"
        odom.twist.twist = Twist(Vector3(0, 0, 0), Vector3(0, 0, 0))

        # publish the message
        new_gps_pub.publish(odom)

        last_time = current_time

        rate.sleep()


    try:
        rospy.spin()
    except KeyboardInterrupt:
        print("Shutting down - Keyboard interrupt")
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main(sys.argv)