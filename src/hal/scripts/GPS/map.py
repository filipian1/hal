#!/usr/bin/env python

import rospy
import numpy as numpy
from std_msgs.msg import Float32MultiArray
import cv2

class map_generator:
    def __init__(self):
        pub=rospy.Publisher("distance_from_goal", Float32MultiArray)
        sub=rospy.Subscriber("GPS1/Coordinates", Float32MultiArray, callback)


    def loadTheMap(self, gps_cords):
        img=cv2.imread("map.png")
        cordL


        return img

    def callback(self, data):
        gps1_cords=data.data

        map_img=loadTheMap(gps1_cords)

        cv2.imshow('Navigation_map',map_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        
        
def main(args):
    mg=map_generator()


    try:
        rospy.spin()
    except KeyboardInterrupt:
        print("Shutting down - Keyboard interrupt")
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main(sys.argv)
