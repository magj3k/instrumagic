from math import *
import numpy as np

class PlaybackSystem(object):
    def __init__(self, synth, audio):
        self.synth = synth
        self.audio = audio

        self.previous_note = None
        self.t = 0

    def on_update(self, dt):
        self.t += dt

        self.audio.on_update()

    def play_sound(self, instrument = "tick"):
        if self.previous_note != None: self.synth.noteoff(self.channel, self.previous_note)

        patch = (128, 0)
        note = 37
        velocity = 75

        if instrument == "piano":
            patch = (0, 2)
            note = 60
            velocity = 80
        elif instrument == "drums":
            patch = (128, 8)
            note = 40
            velocity = 100

        self.synth.program(self.channel, patch[0], patch[1])
        self.synth.noteon(self.channel, note, velocity)
        self.previous_note = note