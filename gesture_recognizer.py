# from kinect import *
from leaputil import *

import Leap
import numpy as np

'''
KINECT INSTALL INSTRUCTIONS:
- http://blog.nelga.com/setup-microsoft-kinect-on-mac-os-x-10-8-mountain-lion/


'''

class GestureRecognizer(object):
    def __init__(self):
        self.leap = Leap.Controller()
        # self.kinect = Kinect()
        # self.kinect.add_joint(Kinect.kRightHand)
        # self.kinect.add_joint(Kinect.kLeftHand)

    def on_update(self) :
        # self.kinect.on_update()

        leap_frame = self.leap.frame()
        left_palm, right_palm = leap_two_palms(leap_frame)
        left_fingers = leap_fingers_frame(leap_frame, "left")
        right_fingers = leap_fingers_frame(leap_frame, "right")

        # print(str(left_palm)+", "+str(right_palm))
        print("\nleft_fingers: "+str(left_fingers))
        print("\nright_fingers: "+str(right_fingers))