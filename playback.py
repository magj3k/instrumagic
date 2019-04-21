from math import *
import numpy as np

from common.core import *
from common.audio import *
from common.synth import *
from common.gfxutil import *
from common.clock import *
from common.metro import *
from common.mixer import *

class PlaybackSystem(object):
    def __init__(self, audio, tempo_map, tempo_processor):
        self.channel = 0

        self.audio = audio
        self.tempo_map = tempo_map
        self.tempo_processor = tempo_processor

        self.mixer = Mixer()
        self.metro_synth = Synth('sfx/FluidR3_GM.sf2')
        self.previous_note_metro = None
        self.mixer.add(self.metro_synth)
        self.performance_synth = Synth('sfx/FluidR3_GM.sf2')
        self.previous_note = None
        self.mixer.add(self.performance_synth)

        # self.sched = AudioScheduler(self.tempo_map)
        self.audio.set_generator(self.mixer)
        # self.sched.set_generator(self.synth)
        # self.metro = Metronome(self.sched, self.synth)

        self.current_measure = 0
        self.current_beat = 0
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
        patch = (128, 0)
        if instrument == "piano":
            patch = (0, 2)
        elif instrument == "drums":
            patch = (128, 8)

        if instrument == "tick":
            if self.previous_note_metro != None: self.metro_synth.noteoff(self.channel, self.previous_note_metro)
            self.metro_synth.program(self.channel, patch[0], patch[1])
            self.metro_synth.noteon(self.channel, pitch, velocity)
            self.previous_note_metro = pitch
        else:
            if self.previous_note != None: self.performance_synth.noteoff(self.channel, self.previous_note)
            self.performance_synth.program(self.channel, patch[0], patch[1])
            self.performance_synth.noteon(self.channel, pitch, velocity)
            self.previous_note = pitch
