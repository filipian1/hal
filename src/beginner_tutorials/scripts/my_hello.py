#!/usr/bin/env python

import cv2
import numpy as np




def say(name):
    print("Hello my dearest " +name)
    img = cv2.imread('src/beginner_tutorials/images/DSC00116.JPG',0)
  
    

    cv2.imshow('zdjatko', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    

if __name__ == '__main__':
    say('Ola')