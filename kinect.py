"""Kinect interface with video, depth stream, and skeletal tracking"""

import thread
import itertools
import ctypes
import sys
from threading import Timer
import time
import math
import numpy as np

from pykinect import nui
from pykinect.nui import JointId, SkeletonTrackingState, TransformSmoothParameters

import pygame
from pygame.color import THECOLORS
from pygame.locals import *

from matplotlib import pyplot as plt

KINECTEVENT = pygame.USEREVENT
DEPTH_WINSIZE = 640,480
VIDEO_WINSIZE = 640,480
SAMPLE_RATE = 30

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

        Timer(.01, self.update_skeleton).start()

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

def unit_vector(v):
    return v / np.linalg.norm(v)

def angle(u, v):
    return np.arccos(np.clip(np.dot(unit_vector(u), unit_vector(v)), -1, 1))

SAMPLE_RATE = 30

class Beat:
    def __init__(self, pos, vel):
        self.pos = pos
        self.vel = vel

class JointModel:
    def __init__(self):
        self.alpha_vel = 0.8
        self.alpha_acc = 0.8
        self.alpha_recent_vel = 0.4
        self.beat_vel_thresh = 0.1
        self.beat_acc_ratio_thresh = 0.8
        
        self.pos = None
        self.vel = None
        self.acc = None
        self.recent_vel = None
        
        self.beat = None
        self.ongoing_beat_vel = None

    def update(self, pos):
        if pos is None:
            vel = None
            acc = None
            recent_vel = None
        elif self.pos is None:
            pos = np.array([pos.x, pos.y, pos.z])
            vel = np.zeros(3)
            acc = np.zeros(3)
            recent_vel = np.zeros(3)
        else:
            pos = np.array([pos.x, pos.y, pos.z])
            vel = self.alpha_vel * SAMPLE_RATE * (pos - self.pos) + (1 - self.alpha_vel) * self.vel
            acc = self.alpha_acc * SAMPLE_RATE * (vel - self.vel) + (1 - self.alpha_acc) * self.acc
            recent_vel = self.alpha_recent_vel * vel + (1 - self.alpha_recent_vel) * self.recent_vel

        if self.recent_vel is not None and acc is not None and \
                np.linalg.norm(self.recent_vel) > self.beat_vel_thresh and \
                np.dot(vel - self.recent_vel, -unit_vector(self.recent_vel)) > self.beat_acc_ratio_thresh * np.linalg.norm(self.recent_vel):
            if self.ongoing_beat_vel is None or angle(self.recent_vel, self.ongoing_beat_vel) > math.pi / 2:
                self.beat = Beat(pos, self.recent_vel)
            else:
                self.beat = None
            self.ongoing_beat_vel = self.recent_vel
        else:
            self.beat = self.ongoing_beat_vel = None

        self.pos, self.vel, self.acc, self.recent_vel = pos, vel, acc, recent_vel

    def downbeat(self):
        return self.beat is not None and -self.beat.vel[1] >= np.max(np.abs(self.beat.vel))

    def upbeat(self):
        return self.beat is not None and self.beat.vel[1] >= np.max(np.abs(self.beat.vel))

    def rightbeat(self):
        return self.beat is not None and self.beat.vel[0] >= np.max(np.abs(self.beat.vel))

    def leftbeat(self):
        return self.beat is not None and -self.beat.vel[0] >= np.max(np.abs(self.beat.vel))

    def frontbeat(self):
        return self.beat is not None and -self.beat.vel[2] >= np.max(np.abs(self.beat.vel))

    def backbeat(self):
        return self.beat is not None and self.beat.vel[2] >= np.max(np.abs(self.beat.vel))

    def active(self):
        return (self.vel is not None and np.linalg.norm(self.vel) > 0.2) or (self.recent_vel is not None and np.linalg.norm(self.recent_vel) > 0.2)


TRACKED_JOINTS = [JointId.HandRight, JointId.HandLeft]

class SkeletonModel:
    def __init__(self):
        self.joints = {}
        for joint in TRACKED_JOINTS:
            self[joint] = JointModel()

    def __getitem__(self, index):
        return self.joints[index]

    def __setitem__(self, index, value):
        self.joints[index] = value

    def update(self, skeleton):
        if skeleton is None:
            for joint in TRACKED_JOINTS:
                self[joint].update(None)
        else:
            for joint in TRACKED_JOINTS:
                self[joint].update(skeleton[joint])


################################################
"""DON'T TOUCH CODE ON TOP OF THIS OR CHRIS WILL..."""
################################################

class skeleton_acceleration:

    def __init__(self):

        self.N=3 
        self.hand_r_positions = [None for i in range(self.N+1)]
        self.hand_r_acce = None #acceleration

        self.hand_l_positions = [None for i in range(self.N+1)]
        self.hand_l_acce = None #acceleration
        
        self.elbow_r = None #position
        self.elbow_l = None #position

        self.DRUM_R = False #initialized motion for it
        self.DRUM_L = False

    def acceleration_update(self, skeleton): #based on acceleration, but general (do helper inside)
        acceleration(skeleton[JointId.HandRight].y, self.hand_r_positions)

    def return_gesture(self): #check accelerations, elbow positions, return motion
        return None
"""
^^^leave this there for me, I'll come back to it.
I need a list of everything I need to keep track first:
drum: hand acceleration - vel down, then 
guitar: hand acceleration + elbow positions (need x coordinates of hands too)
piano: ((maybe same as drum, but same time hands))
^^ but also, lower volume is both hands going down, slower?
raising volume: 
"""





N=3 #number of frames between acceleration measure
past_positions = [None for i in range(N+1)]
DRUM_R = False
def acceleration(position, past_positions=past_positions):
    instan_acceler = None 
    
    #Update past N positions
    for i in range(N):
        past_positions[i] = past_positions[i+1]
    past_positions[N] = position

    if None not in past_positions:
        dp = position - past_positions[0]
        instan_acceler = 900*dp/(N**2)

    return instan_acceler

skeleton_model = SkeletonModel()
def printer(skeleton):
    skeleton_model.update(skeleton)
    audio.on_update()

    if skeleton is None:
        return
    elif (skeleton_model[JointId.HandRight].downbeat() or skeleton_model[JointId.HandLeft].downbeat()) and \
            skeleton_model[JointId.HandRight].ongoing_beat_vel is not None and skeleton_model[JointId.HandLeft].ongoing_beat_vel is not None and \
            abs(skeleton[JointId.HandRight].y - skeleton[JointId.HandLeft].y) < 0.2:
        print('PPPPPPPPPPPPPPPPPPPPPPPPP')
        play_sound('piano', (skeleton_model[JointId.HandRight].ongoing_beat_vel + skeleton_model[JointId.HandLeft].ongoing_beat_vel) / 2)
    elif not skeleton_model[JointId.HandLeft].active() and \
                skeleton[JointId.HandLeft].x - skeleton[JointId.ShoulderLeft].x < -0.02 and skeleton[JointId.HandLeft].y - skeleton[JointId.ShoulderLeft].y > -0.05:
        if (skeleton_model[JointId.HandRight].downbeat() or skeleton_model[JointId.HandRight].upbeat()) and \
                abs(skeleton[JointId.HandRight].x - skeleton[JointId.HipCenter].x) < 0.4 and abs(skeleton[JointId.HandRight].y - skeleton[JointId.HipCenter].y) < 0.4:
            print('-------------------------')
            play_sound('guitar', skeleton_model[JointId.HandRight].beat.vel)
    elif not skeleton_model[JointId.HandLeft].active() and \
                skeleton[JointId.HandRight].x - skeleton[JointId.ShoulderRight].x > 0.02 and skeleton[JointId.HandRight].y - skeleton[JointId.ShoulderRight].y > -0.05:
        if (skeleton_model[JointId.HandLeft].downbeat() or skeleton_model[JointId.HandLeft].upbeat()) and \
                abs(skeleton[JointId.HandLeft].x - skeleton[JointId.HipCenter].x) < 0.4 and abs(skeleton[JointId.HandLeft].y - skeleton[JointId.HipCenter].y) < 0.4:
            print('-------------------------')
            play_sound('guitar', skeleton_model[JointId.HandLeft].beat.vel)
    else:
        if skeleton_model[JointId.HandRight].downbeat():
            play_sound('bass drums', skeleton_model[JointId.HandRight].beat.vel)
        if skeleton_model[JointId.HandLeft].downbeat():
            play_sound('bass drums', skeleton_model[JointId.HandLeft].beat.vel)
        if skeleton_model[JointId.HandRight].frontbeat():
            play_sound('drums', skeleton_model[JointId.HandRight].beat.vel)
        if skeleton_model[JointId.HandLeft].frontbeat():
            play_sound('drums', skeleton_model[JointId.HandLeft].beat.vel)
        if skeleton_model[JointId.HandRight].rightbeat():
            play_sound('tick', skeleton_model[JointId.HandRight].beat.vel)
        if skeleton_model[JointId.HandLeft].leftbeat():
            play_sound('tick', skeleton_model[JointId.HandLeft].beat.vel)


    '''
    if skeleton_model[JointId.HandRight].vel is not None:
        pass
        #print(skeleton_model[JointId.HandRight].vel[1], skeleton_model[JointId.HandRight].recent_vel[1], skeleton_model[JointId.HandRight].acc[1])
    if skeleton_model[JointId.HandRight].beat is not None and skeleton_model[JointId.HandRight].beat.vel[1] < 0:
        #print(skeleton_model[JointId.HandRight].beat.vel)
        play_sound('tick', skeleton_model[JointId.HandRight].beat.vel)
    else:
        pass
        print()
    if skeleton_model[JointId.HandLeft].beat is not None and skeleton_model[JointId.HandLeft].beat.vel[1] < 0:
        #pass
        #print(skeleton_model[JointId.HandLeft].beat.vel)
        play_sound('drums', skeleton_model[JointId.HandLeft].beat.vel)
    #if skeleton_model[JointId.HandRight].vel is not None and np.linalg.norm(skeleton_model[JointId.HandRight].vel) > 1:
     #   print(skeleton_model[JointId.HandRight].vel)
    else:
        pass
        #print()
    '''
    '''
    global DRUM_R 
    if skeleton is None:
        # print('oops')
        accel = acceleration(None)
    else:
        # print(skeleton[JointId.HandRight].y)
        accel = acceleration(skeleton[JointId.HandRight].y)

    #print(accel)

    #What is a drump
    if accel is not None and accel < -22.0/3:
        DRUM_R = True
        
    if DRUM_R and accel > -10.0/3:
            print("drum right")
            DRUM_R = False
    '''
    sys.stdout.flush()
"""
you can play with parameters:
N, and threshold values for drumps

I was counting my drumps and this keeps track of allf
for me. Give it a try! I think this gives me a first idea
for how to develop a class to detect gestures using a few past
positions of hands and elbows. We can talk about it when you are back
"""

from common.core import *
from common.audio import *
from common.synth import *
from common.gfxutil import *
from common.clock import *
from common.metro import *

previous_note = None
channel = 0
audio = Audio(2)
synth = Synth('sfx/FluidR3_GM.sf2')
tempo_map  = SimpleTempoMap(1200)
sched = AudioScheduler(tempo_map)
audio.set_generator(sched)
sched.set_generator(synth)

def play_sound(instrument, vel):
    global previous_note
    if previous_note != None: synth.noteoff(channel, previous_note)

    if instrument == "piano":
        patch = (0, 2)
        note = 60
        velocity = min(120, 50 + int(100 * np.linalg.norm(vel)))
    if instrument == "guitar":
        patch = (0, 26)
        note = 60
        velocity = min(120, 50 + int(100 * np.linalg.norm(vel)))
    elif instrument == "drums":
        patch = (128, 8)
        note = 40
        velocity = min(120, 50 + int(100 * np.linalg.norm(vel)))
    elif instrument == "tick":
        patch = (128, 0)
        note = 37
        velocity = min(120, 50 + int(100 * np.linalg.norm(vel)))
    elif instrument == "bass drums":
        patch = (8, 116)
        note = 20
        velocity = min(120, 50 + int(100 * np.linalg.norm(vel)))
    
    synth.program(channel, patch[0], patch[1])
    synth.noteon(channel, note, velocity)
    previous_note = note

if __name__ == '__main__':
    fig, ax = plt.subplots(1, 1)

    kinect = Kinect(1, True)
    kinect.add_listener(printer)
    kinect.start()

    while True:
        pass
