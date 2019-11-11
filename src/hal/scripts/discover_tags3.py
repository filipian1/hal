#!/usr/bin/env python

import rospy
from rospy_tutorials.msg import Floats
from rospy.numpy_msg import numpy_msg
from sensor_msgs.msg import Image
import cv2
import sys
from cv_bridge import CvBridge, CvBridgeError
import numpy as np

from matplotlib import pyplot as plt
import copy
import imutils
import math

class image_converter:

    def __init__(self):
        self.image_pub = rospy.Publisher("/camera/image_opencv", numpy_msg(Floats), queue_size=10)
        self.bridge=CvBridge()
        self.image_sub = rospy.Subscriber("/camera/image_raw", Image , self.callback)
        global p1

        # Decode the tag ID and 4 digit binary and orientation
    def id_decode(self, image):
        ret, img_bw = cv2.threshold(image, 200, 255, cv2.THRESH_BINARY)
        corner_pixel = 255
        cropped_img = img_bw[50:150, 50:150]

        block_1 = cropped_img[37, 37]
        block_3 = cropped_img[62, 37]
        block_2 = cropped_img[37, 62]
        block_4 = cropped_img[62, 62]
        white = 255
        if block_3 == white:
            block_3 = 1
        else:
            block_3 = 0
        if block_4 == white:
            block_4 = 1
        else:
            block_4 = 0
        if block_2 == white:
            block_2 = 1
        else:
            block_2 = 0
        if block_1 == white:
            block_1 = 1
        else:
            block_1 = 0

        if cropped_img[85, 85] == corner_pixel:
            return list([block_3, block_4, block_2, block_1]), "BR"
        elif cropped_img[15, 85] == corner_pixel:
            return list([block_4, block_2, block_1, block_3]), "TR"
        elif cropped_img[15, 15] == corner_pixel:
            return list([block_2, block_1, block_3, block_4]), "TL"
        elif cropped_img[85, 15] == corner_pixel:
            return list([block_1, block_3, block_4, block_2]), "BL"

        return None, None


  

    # Generate contours to detect corners of the tag
    def contour_generator(self, frame):
        test_img1 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        test_blur = cv2.GaussianBlur(test_img1, (5, 5), 0)
        edge = cv2.Canny(test_blur, 75, 200)
        edge1 = copy.copy(edge)
        contour_list = list()

        r, cnts, h = cv2.findContours(edge1, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        index = list()
        for hier in h[0]:
            if hier[3] != -1:
                index.append(hier[3])

        # loop over the contours
        for c in index:
            peri = cv2.arcLength(cnts[c], True)
            approx = cv2.approxPolyDP(cnts[c], 0.02 * peri, True)

            if len(approx) > 4:
                peri1 = cv2.arcLength(cnts[c - 1], True)
                corners = cv2.approxPolyDP(cnts[c - 1], 0.02 * peri1, True)
                contour_list.append(corners)

        new_contour_list = list()
        for contour in contour_list:
            if len(contour) == 4:
                new_contour_list.append(contour)
        final_contour_list = list()
        for element in new_contour_list:
            if cv2.contourArea(element) < 2500:
                final_contour_list.append(element)

        return final_contour_list

        
    def callback(self,data):
        # rospy.loginfo(rospy.get_caller_id() + "I heard an image %s"%str(data.data))
        
        try:
            cv_image = self.bridge.imgmsg_to_cv2(data)
        except CvBridgeError as e:
            print(e)

        frame = cv_image

        final_contour_list = self.contour_generator(frame)


        for i in range(len(final_contour_list)):
            cv2.drawContours(frame, [final_contour_list[i]], -1, (0, 255, 0), 2)
            cv2.imshow("Outline", frame)

        if cv2.waitKey(1) & 0xff == 27:
            cv2.destroyAllWindows()



        
def main(args):
  
    rospy.init_node('image_converter_ROS2CV', anonymous=True)

    # dim=200
    # p1 = np.array([
    # [0, 0],
    # [dim - 1, 0],
    # [dim - 1, dim - 1],
    # [0, dim - 1]], dtype="float32")

    ic=image_converter()
    try:
        rospy.spin()
    except KeyboardInterrupt:
        print("Shutting down - Keyboard interrupt")
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main(sys.argv)

    
