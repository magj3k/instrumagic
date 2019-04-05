from math import *
import numpy as np

class PlaybackSystem(object):
    def __init__(self, t=0, beat_callback=None):
        self.t = t
        self.beats_per_minute = 100
        self.current_beat = 0

        self.beat_callback = beat_callback

    def quantize_time_to_beat(self, time, round_up=True):
        bps = self.beats_per_minute/60.0
        beat = int(ceil(time * bps))
        if round_up == False: beat = int(round(time * bps))
        return beat

    def on_update(self, dt=0.1):
        self.t += dt

        beat = self.quantize_time_to_beat(self.t, False)
        if beat != self.current_beat:
            self.current_beat = beat
            if self.beat_callback != None: self.beat_callback(self.current_beat)

            if self.current_beat % 4 == 0: print("BEAT: "+str(self.current_beat))