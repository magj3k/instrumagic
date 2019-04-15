"""Kinect interface with video, depth stream, and skeletal tracking"""

import thread
import itertools
import ctypes
import sys
from threading import Timer
import time

from pykinect import nui
from pykinect.nui import JointId, SkeletonTrackingState

import pygame
from pygame.color import THECOLORS
from pygame.locals import *

from matplotlib import pyplot as plt

KINECTEVENT = pygame.USEREVENT
DEPTH_WINSIZE = 640,480
VIDEO_WINSIZE = 640,480

SKELETON_COLORS = [THECOLORS["red"], 
                   THECOLORS["blue"], 
                   THECOLORS["green"], 
                   THECOLORS["orange"], 
                   THECOLORS["purple"], 
                   THECOLORS["yellow"], 
                   THECOLORS["violet"]]

LEFT_ARM = (JointId.ShoulderCenter, 
            JointId.ShoulderLeft, 
            JointId.ElbowLeft, 
            JointId.WristLeft, 
            JointId.HandLeft)
RIGHT_ARM = (JointId.ShoulderCenter, 
             JointId.ShoulderRight, 
             JointId.ElbowRight, 
             JointId.WristRight, 
             JointId.HandRight)
LEFT_LEG = (JointId.HipCenter, 
            JointId.HipLeft, 
            JointId.KneeLeft, 
            JointId.AnkleLeft, 
            JointId.FootLeft)
RIGHT_LEG = (JointId.HipCenter, 
             JointId.HipRight, 
             JointId.KneeRight, 
             JointId.AnkleRight, 
             JointId.FootRight)
SPINE = (JointId.HipCenter, 
         JointId.Spine, 
         JointId.ShoulderCenter, 
         JointId.Head)

skeleton_to_depth_image = nui.SkeletonEngine.skeleton_to_depth_image

# recipe to get address of surface: http://archives.seul.org/pygame/users/Apr-2008/msg00218.html
if hasattr(ctypes.pythonapi, 'Py_InitModule4'):
   Py_ssize_t = ctypes.c_int
elif hasattr(ctypes.pythonapi, 'Py_InitModule4_64'):
   Py_ssize_t = ctypes.c_int64
else:
   raise TypeError("Cannot determine type of Py_ssize_t")

_PyObject_AsWriteBuffer = ctypes.pythonapi.PyObject_AsWriteBuffer
_PyObject_AsWriteBuffer.restype = ctypes.c_int
_PyObject_AsWriteBuffer.argtypes = [ctypes.py_object,
                                  ctypes.POINTER(ctypes.c_void_p),
                                  ctypes.POINTER(Py_ssize_t)]

def surface_to_array(surface):
   buffer_interface = surface.get_buffer()
   address = ctypes.c_void_p()
   size = Py_ssize_t()
   _PyObject_AsWriteBuffer(buffer_interface,
                          ctypes.byref(address), ctypes.byref(size))
   bytes = (ctypes.c_byte * size.value).from_address(address.value)
   bytes.object = buffer_interface
   return bytes


class Kinect:

    def __init__(self, display=0, draw_skeleton=False, elevation_angle=20):
        self.video_display = display == 1
        self.depth_display = display == 2
        self.draw_skeleton = draw_skeleton
        self.elevation_angle = elevation_angle
        self.listeners = []

    def add_listener(self, callback):
        self.listeners.append(callback)

    def start(self):
        pygame.init()
        self.kinect = nui.Runtime()

        self.kinect.camera.elevation_angle = self.elevation_angle

        self.kinect.skeleton_engine.enabled = True

        if self.video_display or self.depth_display:
            self.screen_lock = thread.allocate()
            self.screen = pygame.display.set_mode(VIDEO_WINSIZE if self.video_display else DEPTH_WINSIZE, 0, 32 if self.video_display else 16)
            pygame.display.set_caption('PyKinect')
            self.skeletons = None
            self.screen.fill(THECOLORS["black"])
            
            if self.video_display:
                self.kinect.video_frame_ready += self.video_frame_ready
                self.kinect.video_stream.open(nui.ImageStreamType.Video, 2, nui.ImageResolution.Resolution640x480, nui.ImageType.Color)
            if self.depth_display:
                self.kinect.depth_frame_ready += self.depth_frame_ready
                self.kinect.depth_stream.open(nui.ImageStreamType.Depth, 2, nui.ImageResolution.Resolution640x480, nui.ImageType.Depth)

        #self.kinect.skeleton_frame_ready += self.post_frame

        self.dispInfo = pygame.display.Info()

        self.update_skeleton()

    def update_skeleton(self):
        try:
            self.skeletons = self.kinect.skeleton_engine.get_next_frame().SkeletonData
        except:
            return

        try:
            skeleton = next(skeleton.SkeletonPositions for skeleton in self.skeletons if skeleton.eTrackingState == SkeletonTrackingState.TRACKED)
        except:
            skeleton = None

        for listener in self.listeners:
            listener(skeleton)

        if self.draw_skeleton:
            self.draw_skeletons(self.skeletons)
            pygame.display.update()

        Timer(1.0/30, self.update_skeleton).start()

    def draw_skeleton_data(self, pSkelton, index, positions, width = 4):
        start = pSkelton.SkeletonPositions[positions[0]]
           
        for position in itertools.islice(positions, 1, None):
            next = pSkelton.SkeletonPositions[position.value]
            
            curstart = skeleton_to_depth_image(start, self.dispInfo.current_w, self.dispInfo.current_h) 
            curend = skeleton_to_depth_image(next, self.dispInfo.current_w, self.dispInfo.current_h)

            pygame.draw.line(self.screen, SKELETON_COLORS[index], curstart, curend, width)
            
            start = next

    def draw_skeletons(self, skeletons):
        for index, data in enumerate(skeletons):
            # draw the Head
            HeadPos = skeleton_to_depth_image(data.SkeletonPositions[JointId.Head], self.dispInfo.current_w, self.dispInfo.current_h) 
            self.draw_skeleton_data(data, index, SPINE, 10)
            pygame.draw.circle(self.screen, SKELETON_COLORS[index], (int(HeadPos[0]), int(HeadPos[1])), 20, 0)
        
            # drawing the limbs
            self.draw_skeleton_data(data, index, LEFT_ARM)
            self.draw_skeleton_data(data, index, RIGHT_ARM)
            self.draw_skeleton_data(data, index, LEFT_LEG)
            self.draw_skeleton_data(data, index, RIGHT_LEG)


    def depth_frame_ready(self, frame):
        if not self.depth_display:
            return

        with self.screen_lock:
            address = surface_to_array(self.screen)
            frame.image.copy_bits(address)
            del address
            if self.skeletons is not None and self.draw_skeleton:
                self.draw_skeletons(self.skeletons)
            pygame.display.update()    


    def video_frame_ready(self, frame):
        if not self.video_display:
            return

        with self.screen_lock:
            address = surface_to_array(self.screen)
            frame.image.copy_bits(address)
            del address
            if self.skeletons is not None and self.draw_skeleton:
                self.draw_skeletons(self.skeletons)
            pygame.display.update()

    def post_frame(self, frame):
        try:
            skeleton = next(skeleton.SkeletonPositions for skeleton in frame.SkeletonData if skeleton.eTrackingState == SkeletonTrackingState.TRACKED)
        except:
            return

        for listener in self.listeners:
            listener(skeleton)

        self.skeletons = frame.SkeletonData
        if self.draw_skeleton:
            self.draw_skeletons(self.skeletons)
            pygame.display.update()


def printer(skeleton):
    if skeleton is None:
        print('oops')
    else:
        print(skeleton[JointId.HandRight].y)
    sys.stdout.flush()

if __name__ == '__main__':
    fig, ax = plt.subplots(1, 1)

    kinect = Kinect(1, True)
    kinect.add_listener(printer)
    kinect.start()

    while True:
        pass
