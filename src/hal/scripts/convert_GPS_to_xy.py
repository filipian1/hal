#!/usr/bin/env python

import rospy
import numpy as numpy
from nav_msgs.msg import Odometry 
from sensor_msgs.msg import NavSatFix
from geometry_msgs.msg import Point, Pose, Quaternion, Twist, Vector3Stamped, Vector3
import tf
import sys
import pyproj

gps_coord_x = None
gps_coord_y = None
gps_vel=None

def callback(nav_gps):
    global z,l, gps_coord_x, gps_coord_y
    x_offset=5527517.1375682
    y_offset=492818.458753

    z,l, gps_coord_y, gps_coord_x=project((nav_gps.longitude,nav_gps.latitude))
    gps_coord_x-=x_offset
    gps_coord_y*=-1
    gps_coord_y+=y_offset
    



def callbackVel(nav_gps_speed):
    global gps_vel
    gps_vel=nav_gps_speed.vector.x
    


_projections = {}


def zone(coordinates):
    if 56 <= coordinates[1] < 64 and 3 <= coordinates[0] < 12:
        return 32
    if 72 <= coordinates[1] < 84 and 0 <= coordinates[0] < 42:
        if coordinates[0] < 9:
            return 31
        elif coordinates[0] < 21:
            return 33
        elif coordinates[0] < 33:
            return 35
        return 37
    return int((coordinates[0] + 180) / 6) + 1


def letter(coordinates):
    return 'CDEFGHJKLMNPQRSTUVWXX'[int((coordinates[1] + 80) / 8)]


def project(coordinates):
    z = zone(coordinates)
    l = letter(coordinates)
    if z not in _projections:
        _projections[z] = pyproj.Proj(proj='utm', zone=z, ellps='WGS84')
    x, y = _projections[z](coordinates[0], coordinates[1])
    if y < 0:
        y += 10000000
    return z, l, x, y


def unproject(z, l, x, y):
    if z not in _projections:
        _projections[z] = pyproj.Proj(proj='utm', zone=z, ellps='WGS84')
    if l < 'N':
        y -= 10000000
    lng, lat = _projections[z](x, y, inverse=True)
    return (lng, lat)
       
        
def main(args):
    rospy.init_node('gps_odom_covnerter', anonymous=True)
   
    new_gps_pub=rospy.Publisher("odometry/gps/converted", Odometry, queue_size=10)
    gps_sub=rospy.Subscriber("fix", NavSatFix, callback)
    gps_vel_sub=rospy.Subscriber("fix_velocity", Vector3Stamped, callbackVel)

    
    
    # current_time = rospy.Time.now()
    # last_time = rospy.Time.now() 


    rate = rospy.Rate(1)
    while not rospy.is_shutdown():

        seconds=rospy.get_time()
        
        odom_quat = tf.transformations.quaternion_from_euler(0, 0, 0)

        odom = Odometry()
        odom.header.stamp.secs = seconds
        odom.header.frame_id = "map"

        # set the position
        odom.pose.pose = Pose(Point(gps_coord_x, gps_coord_y, 0), Quaternion(*odom_quat))

        # set the velocity
        # odom.child_frame_id = "base_footprint"
        odom.twist.twist = Twist(Vector3(gps_vel,0 ,0), Vector3(0, 0, 0))

        # publish the message
        new_gps_pub.publish(odom)

        # last_time = current_time

        rate.sleep()


    try:
        rospy.spin()
    except KeyboardInterrupt:
        print("Shutting down - Keyboard interrupt")
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main(sys.argv)