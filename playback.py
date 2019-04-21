from math import *
import numpy as np

from common.core import *
from common.audio import *
from common.synth import *
from common.gfxutil import *
from common.clock import *
from common.metro import *

class PlaybackSystem(object):
    def __init__(self, synth, audio, tempo_map, tempo_processor):
        self.channel = 0

        self.synth = synth
        self.audio = audio
        self.tempo_map = tempo_map
        self.tempo_processor = tempo_processor

        self.sched = AudioScheduler(self.tempo_map)
        self.audio.set_generator(self.sched)
        self.sched.set_generator(self.synth)
        # self.metro = Metronome(self.sched, self.synth)

        self.current_measure = 0
        self.current_beat = 0
        self.previous_note = None
        self.t = 0

        # self.metro.start()

    def on_update(self, dt):
        self.t += dt
        self.audio.on_update()

        measure = self.tempo_processor.current_beat(4)
        beat = self.tempo_processor.current_beat()
        if self.current_beat != beat:
            self.current_beat = beat
            self.current_measure = measure

            if self.current_beat % 4 == 0:
                if measure == 0:
                    self.play_sound("tick", 45, 90)
                else:
                    self.play_sound("tick", 45, 75)
            else:
                self.play_sound("tick", 45, 50)

    def play_sound(self, instrument = "tick", pitch = 45, velocity = 75):
        if self.previous_note != None: self.synth.noteoff(self.channel, self.previous_note)

        patch = (128, 0)
        if instrument == "piano":
            patch = (0, 2)
        elif instrument == "drums":
            patch = (128, 8)

        self.synth.program(self.channel, patch[0], patch[1])
        self.synth.noteon(self.channel, pitch, velocity)
        self.previous_note = pitch
