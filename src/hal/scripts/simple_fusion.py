#!/usr/bin/env python

import rospy
import numpy as numpy
from nav_msgs.msg import Odometry 
from sensor_msgs.msg import NavSatFix, Imu
from geometry_msgs.msg import Point, Pose, Quaternion, Twist, Vector3
import tf
import sys
import pyproj

gps_coord_x = None
gps_coord_y = None
imu_orientation=list()
angular_velocity=list()
linear_velocity=list()

def callbackGPS(gps_odom):
    global gps_coord_x, gps_coord_y
    gps_coord_x=gps_odom.pose.pose.position.x
    gps_coord_y=gps_odom.pose.pose.position.y


def callbackIMU(imu_data):
    global imu_orientation, angular_velocity
    imu_orientation=list()
    angular_velocity=list()

    imu_orientation.append(imu_data.orientation.x)
    imu_orientation.append(imu_data.orientation.y)
    imu_orientation.append(imu_data.orientation.z)
    imu_orientation.append(imu_data.orientation.w)

    angular_velocity.append(imu_data.angular_velocity.x)
    angular_velocity.append(imu_data.angular_velocity.y)
    angular_velocity.append(imu_data.angular_velocity.z)

def callbackOdom(wheel_odom):
    global linear_velocity
    linear_velocity=list()

    linear_velocity.append(wheel_odom.twist.twist.linear.x)
    linear_velocity.append(wheel_odom.twist.twist.linear.y)
    linear_velocity.append(wheel_odom.twist.twist.linear.z)




def main(args):
    rospy.init_node('simple_fusion', anonymous=False)
   
    new_gps_pub=rospy.Publisher("odometry/simple", Odometry, queue_size=10)
    imu_sub=rospy.Subscriber("imu/data", Imu, callbackIMU)
    gps_sub=rospy.Subscriber("odometry/gps/converted", Odometry, callbackGPS)
    odom_sub=rospy.Subscriber("my1model_diff_drive_controller/odom", Odometry, callbackOdom)
   


    current_time = rospy.Time.now()
    last_time = rospy.Time.now() 


    rate = rospy.Rate(10)
    while not rospy.is_shutdown():

        odom_quat = tf.transformations.quaternion_from_euler(0, 0, 0)
        

        odom = Odometry()
        odom.header.stamp = current_time
        odom.header.frame_id = "map"

        

        # set the position
        odom.pose.pose = Pose(Point(gps_coord_x, gps_coord_y, 0), Quaternion(*imu_orientation))

        # set the velocity
        odom.child_frame_id = "base_footprint"
        odom.twist.twist = Twist(Vector3(*linear_velocity), Vector3(*angular_velocity))

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