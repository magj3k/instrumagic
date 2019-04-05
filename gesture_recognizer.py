# from kinect import *
from leaputil import *

import Leap
import numpy as np

class GestureRecognizer(object):
    def __init__(self, playback_system):
        self.leap = Leap.Controller()
        self.playback_system = playback_system

        self.gesture_timeouts = {
            "leftfist": 0,
            "leftpiano": 0,
            "leftup_conduct": 0,
            "leftdown_conduct": 0,
            "rightfist": 0,
            "rightpiano": 0,
            "rightup_conduct": 0,
            "rightdown_conduct": 0
        }

        self.t = 0
        self.speed_timespan = 0.125 # in seconds
        self.acceleration_timespan = 0.125 # in seconds
        self.acceleration_stop_timespan = 0.07 # in seconds
        self.acceleration_threshold = 45000
        self.acceleration_stop_threshold = 900

        self.left_hand_available = False
        self.right_hand_available = False
        self.left_palm_pos_over_time = []
        self.right_palm_pos_over_time = []
        self.left_palm_vel_over_time = []
        self.right_palm_vel_over_time = []

        self.clustered_left_palm_acc = []
        self.clustered_right_palm_acc = []

        self.left_palm_velocity = 0.0
        self.right_palm_velocity = 0.0
        self.left_palm_acceleration = 0.0
        self.right_palm_acceleration = 0.0

    def finger_span(self, fingers):
        min_x = -1
        min_y = -1
        min_z = -1
        max_x = -1
        max_y = -1
        max_z = -1
        for finger in fingers:
            if min_x == -1:
                min_x = finger[0]
            if max_x == -1:
                max_x = finger[0]

            if min_y == -1:
                min_y = finger[1]
            if max_y == -1:
                max_y = finger[1]

            if min_z == -1:
                min_z = finger[2]
            if max_z == -1:
                max_z = finger[2]

            min_x = min(min_x, finger[0])
            max_x = max(max_x, finger[0])
            min_y = min(min_y, finger[1])
            max_y = max(max_y, finger[1])
            min_z = min(min_z, finger[2])
            max_z = max(max_z, finger[2])

        return [max_x-min_x, max_y-min_y, max_z-min_z]

    def classify_hand(self, side, palm_position, fingers):
        fin_span = self.finger_span(fingers)
        # print("HAND POS: "+str(palm_position))
        # print("FINGERS: "+str(fingers))
        # print("FIN SPAN: "+str(fin_span))

        # classifying fist
        if self.gesture_timeouts[side+"fist"] <= 0.0 and fin_span[0] < 55.0 and fin_span[1] < 45.0 and fin_span[2] < 45.0 and palm_position[1] > 130.0:
            self.gesture_timeouts[side+"fist"] = 0.35
            return "fist"

        # classifying upward conducting stroke
        if self.gesture_timeouts[side+"up_conduct"] <= 0.0 and palm_position[1] > 270.0:
            if fin_span[0] < 55.0:
                self.gesture_timeouts[side+"up_conduct"] = 1.0
                self.gesture_timeouts[side+"down_conduct"] = 0.5
                return "up_conduct"

        # classifying downward conducting stroke
        if self.gesture_timeouts[side+"down_conduct"] <= 0.0 and palm_position[1] < 160.0:
            if fin_span[0] < 60.0:
                self.gesture_timeouts[side+"down_conduct"] = 1.0
                self.gesture_timeouts[side+"up_conduct"] = 0.5
                return "down_conduct"

        # classifying piano stroke
        if self.gesture_timeouts[side+"piano"] <= 0.0 and palm_position[1] < 240.0:
            if fin_span[0] > 100.0 and fin_span[1] < 30.0 and fin_span[2] < 92.0:
                self.gesture_timeouts[side+"piano"] = 0.35
                return "piano"

        return "none"

    def gather_leap_data(self):
        leap_frame = self.leap.frame()
        left_palm, right_palm = leap_two_palms(leap_frame)
        left_fingers = leap_fingers_frame(leap_frame, "left")
        right_fingers = leap_fingers_frame(leap_frame, "right")
        return left_palm, right_palm, left_fingers, right_fingers

    def on_update(self, dt=0.1) :
        self.t += dt

        # time management
        for key in self.gesture_timeouts.keys():
            self.gesture_timeouts[key] = max(self.gesture_timeouts[key]-dt, 0.0)

        # gathering raw data from the Leap
        left_palm, right_palm, left_fingers, right_fingers = self.gather_leap_data()

        if len(left_fingers) == 0:
            self.left_hand_available = False
            self.left_palm_pos_over_time = []
        else:
            self.left_hand_available = True

            # stores palm positions over time
            self.left_palm_pos_over_time.append( (left_palm, self.t) )
            if len(self.left_palm_pos_over_time) > 50:
                self.left_palm_pos_over_time = self.left_palm_pos_over_time[1:]

        if len(right_fingers) == 0:
            self.right_hand_available = False
            self.right_palm_pos_over_time = []
        else:
            self.right_hand_available = True

            # stores palm positions over time
            self.right_palm_pos_over_time.append( (right_palm, self.t) )
            if len(self.right_palm_pos_over_time) > 50:
                self.right_palm_pos_over_time = self.right_palm_pos_over_time[1:]

        # calculates velocities of each palm position
        self.left_palm_velocity = np.array((0.0, 0.0, 0.0))
        left_palm_valid_sample_count = 0
        for j in range(len(self.left_palm_pos_over_time)):
            i = len(self.left_palm_pos_over_time)-j-1
            if self.left_palm_pos_over_time[i][1] >= self.t-self.speed_timespan:
                sample = self.left_palm_pos_over_time[i]
                self.left_palm_velocity += (left_palm-sample[0])/(self.t-sample[1]+0.00001)
                left_palm_valid_sample_count += 1
            else:
                break
        self.left_palm_velocity = self.left_palm_velocity / max(left_palm_valid_sample_count, 1)

        self.right_palm_velocity = np.array((0.0, 0.0, 0.0))
        right_palm_valid_sample_count = 0
        for j in range(len(self.right_palm_pos_over_time)):
            i = len(self.right_palm_pos_over_time)-j-1
            if self.right_palm_pos_over_time[i][1] >= self.t-self.speed_timespan:
                sample = self.right_palm_pos_over_time[i]
                self.right_palm_velocity += (right_palm-sample[0])/(self.t-sample[1]+0.00001)
                right_palm_valid_sample_count += 1
            else:
                break
        self.right_palm_velocity = self.right_palm_velocity / max(right_palm_valid_sample_count, 1)
        
        left_palm_velocty_magnitude = np.linalg.norm(self.left_palm_velocity)
        right_palm_velocty_magnitude = np.linalg.norm(self.right_palm_velocity)
        # print("EST left hand vel: "+str(left_palm_velocty_magnitude))

        # calculates acceleration of each palm position using velocity magnitude
        self.left_palm_vel_over_time.append( (left_palm_velocty_magnitude, self.t) )
        if len(self.left_palm_vel_over_time) > 50:
            self.left_palm_vel_over_time = self.left_palm_vel_over_time[1:]
        self.right_palm_vel_over_time.append( (right_palm_velocty_magnitude, self.t) )
        if len(self.right_palm_vel_over_time) > 50:
            self.right_palm_vel_over_time = self.right_palm_vel_over_time[1:]

        self.left_palm_acceleration = 0.0
        left_palm_valid_sample_count = 0
        for j in range(len(self.left_palm_vel_over_time)):
            i = len(self.left_palm_vel_over_time)-j-1
            if self.left_palm_vel_over_time[i][1] >= self.t-self.acceleration_timespan:
                sample = self.left_palm_vel_over_time[i]
                self.left_palm_acceleration += (left_palm_velocty_magnitude-sample[0])/(self.t-sample[1]+0.00001)
                left_palm_valid_sample_count += 1
            else:
                break
        self.left_palm_acceleration = self.left_palm_acceleration / max(left_palm_valid_sample_count, 1)

        self.right_palm_acceleration = 0.0
        right_palm_valid_sample_count = 0
        for j in range(len(self.right_palm_vel_over_time)):
            i = len(self.right_palm_vel_over_time)-j-1
            if self.right_palm_vel_over_time[i][1] >= self.t-self.acceleration_timespan:
                sample = self.right_palm_vel_over_time[i]
                self.right_palm_acceleration += (right_palm_velocty_magnitude-sample[0])/(self.t-sample[1]+0.00001)
                right_palm_valid_sample_count += 1
            else:
                break
        self.right_palm_acceleration = self.right_palm_acceleration / max(right_palm_valid_sample_count, 1)

        # if large acceleration occurs, track clustered acceleration points
        if self.left_hand_available == True:
            if np.abs(self.left_palm_acceleration) > self.acceleration_threshold:
                self.clustered_left_palm_acc.append( (self.left_palm_acceleration, self.t) )
            elif np.abs(self.left_palm_acceleration) < self.acceleration_stop_threshold and len(self.clustered_left_palm_acc) > 0 and np.abs(self.clustered_left_palm_acc[-1][1] - self.t) > self.acceleration_stop_timespan:
                self.clustered_left_palm_acc = []

                # if large acceleration stops, quantize beat and classify hand configuration
                hand_classification = self.classify_hand("left", left_palm, left_fingers)
                quantized_beat = max(self.playback_system.quantize_time_to_beat(self.t), self.playback_system.current_beat+1)
                if hand_classification != "none": print("LARGE LEFT ACC: "+str(self.t)+", C: "+str(hand_classification)+", QB: "+str(quantized_beat))

        if self.right_hand_available == True:
            if np.abs(self.right_palm_acceleration) > self.acceleration_threshold:
                self.clustered_right_palm_acc.append( (self.right_palm_acceleration, self.t) )
            elif np.abs(self.right_palm_acceleration) < self.acceleration_stop_threshold and len(self.clustered_right_palm_acc) > 0 and np.abs(self.clustered_right_palm_acc[-1][1] - self.t) > self.acceleration_stop_timespan:
                self.clustered_right_palm_acc = []

                # if large acceleration stops, quantize beat and classify hand configuration
                hand_classification = self.classify_hand("right", right_palm, right_fingers)
                quantized_beat = max(self.playback_system.quantize_time_to_beat(self.t), self.playback_system.current_beat+1)
                if hand_classification != "none": print("LARGE RIGHT ACC: "+str(self.t)+", C: "+str(hand_classification)+", QB: "+str(quantized_beat))
        



