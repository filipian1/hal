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


    # Function to return the order of points in camera frame
    def order(self, pts):
        rect = np.zeros((4, 2), dtype="float32")

        s = pts.sum(axis=1)
        # print(np.argmax(s))
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]

        diff = np.diff(pts, axis=1)
        # print(np.argmax(diff))
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]

        # return the ordered coordinates
        return rect

    # Function to compute homography between world and camera frame 
    def homograph(self, p, p1):
        A = []
        p2 = self.order(p)

        for i in range(0, len(p1)):
            x, y = p1[i][0], p1[i][1]
            u, v = p2[i][0], p2[i][1]
            A.append([x, y, 1, 0, 0, 0, -u * x, -u * y, -u])
            A.append([0, 0, 0, x, y, 1, -v * x, -v * y, -v])
        A = np.array(A)
        U, S, Vh = np.linalg.svd(A)
        l = Vh[-1, :] / Vh[-1, -1]
        h = np.reshape(l, (3, 3))
        # print(l)
        # print(h)
        return h

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

    # Reorient the tag based on the original orientation
    def reorient(self, location, maxDim):
        if location == "BR":
            p1 = np.array([
                [0, 0],
                [maxDim - 1, 0],
                [maxDim - 1, maxDim - 1],
                [0, maxDim - 1]], dtype="float32")
            return p1
        elif location == "TR":
            p1 = np.array([
                [maxDim - 1, 0],
                [maxDim - 1, maxDim - 1],
                [0, maxDim - 1],
                [0, 0]], dtype="float32")
            return p1
        elif location == "TL":
            p1 = np.array([
                [maxDim - 1, maxDim - 1],
                [0, maxDim - 1],
                [0, 0],
                [maxDim - 1, 0]], dtype="float32")
            return p1

        elif location == "BL":
            p1 = np.array([
                [0, maxDim - 1],
                [0, 0],
                [maxDim - 1, 0],
                [maxDim - 1, maxDim - 1]], dtype="float32")
            return p1

        
    def callback(self,data):
        # rospy.loginfo(rospy.get_caller_id() + "I heard an image %s"%str(data.data))
        
        try:
            cv_image = self.bridge.imgmsg_to_cv2(data)
        except CvBridgeError as e:
            print(e)

        # (rows, cols, channels)=cv_image.shape
        # print(cv_image.shape)
        # cv2.circle(cv_image, (100,100), 20, (0,255,0), 5)

        # cv2.imshow("Image in OpenCV", cv_image)
        #cv2.waitKey(3)

        frame = cv_image
        # print(frame)
        # print(type(frame))
        # print(frame.shape)
        final_contour_list = self.contour_generator(frame)


        for i in range(len(final_contour_list)):
            cv2.drawContours(frame, [final_contour_list[i]], -1, (0, 255, 0), 2)
            cv2.imshow("Outline", frame)

# HOMOGRAFIA

#            warped = homogenous_transform(small, final_contour_list[i][:, 0])

#             c_rez = final_contour_list[i][:, 0]
#             H_matrix = self.homograph(p1, self.order(c_rez))

#  #           H_matrix = homo(p1,order(c))
#             tag = cv2.warpPerspective(frame, H_matrix, (200, 200))
#             cv2.imshow("Outline", frame)
#             cv2.imshow("Tag after Homo", tag)


 #Dekodowanie i dodawanie leny
        #     tag1 = cv2.cvtColor(tag, cv2.COLOR_BGR2GRAY)
        #     decoded, location = self.id_decode(tag1)
        #     empty = np.full(frame.shape, 0, dtype='uint8')
        #     if not location == None:
        #         p2 = self.reorient(location, 200)
        #         if not decoded == None:
        #             print("ID detected: " + str(decoded))
        #         H_Lena = self.homograph(order(c_rez), p2)
        #         lena_overlap = cv2.warpPerspective(lena_resize, H_Lena, (frame.shape[1], frame.shape[0]))
        #         if not np.array_equal(lena_overlap, empty):
        #             lena_list.append(lena_overlap.copy())
        #             print(lena_overlap.shape)

        # mask = np.full(frame.shape, 0, dtype='uint8')
        # if lena_list != []:
        #     for lena in lena_list:
        #         temp = cv2.add(mask, lena.copy())
        #         mask = temp

        #     lena_gray = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
        #     r, lena_bin = cv2.threshold(lena_gray, 10, 255, cv2.THRESH_BINARY)

        #     mask_inv = cv2.bitwise_not(lena_bin)

        #     mask_3d = frame.copy()
        #     mask_3d[:, :, 0] = mask_inv
        #     mask_3d[:, :, 1] = mask_inv
        #     mask_3d[:, :, 2] = mask_inv
        #     img_masked = cv2.bitwise_and(frame, mask_3d)
        #     final_image = cv2.add(img_masked, mask)
        #     cv2.imshow("Lena", final_image)
        #     cv2.waitKey(0)

        if cv2.waitKey(1) & 0xff == 27:
            cv2.destroyAllWindows()



        

def main(args):
    global p1
    global lena_list
    lena_list = list()
    rospy.init_node('image_converter_ROS2CV', anonymous=True)

    dim=200
    p1 = np.array([
    [0, 0],
    [dim - 1, 0],
    [dim - 1, dim - 1],
    [0, dim - 1]], dtype="float32")

    ic=image_converter()
    try:
        rospy.spin()
    except KeyboardInterrupt:
        print("Shutting down - Keyboard interrupt")
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main(sys.argv)

    
