from math import *
import numpy as np

from common.core import *
from common.audio import *
from common.synth import *
from common.gfxutil import *
from common.clock import *
from common.metro import *
from common.mixer import *


class Chord(object):
    def __init__(self, pitches):
        pitches.sort()

        self.base = pitches[0]
        self.type = "major"
        if pitches[1] == pitches[0]+3:
            self.type = "minor"
            
    def get_pitches(self):
        pitches = [self.base]
        if self.type == "major":
            pitches.append(self.base+4)
            pitches.append(self.base+7)
        elif self.type == "minor":
            pitches.append(self.base+3)
            pitches.append(self.base+7)
        return pitches

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

        self.audio.set_generator(self.mixer)

        self.current_measure = 0
        self.current_beat = 0
        self.t = 0

        self.chord_progression = [Chord([60, 64]), Chord([55, 59]), Chord([57, 60]), Chord([65, 69])]

    def on_update(self, dt):
        self.t += dt
        self.audio.on_update()

        measure = self.tempo_processor.current_beat(4)
        beat = self.tempo_processor.current_beat()
        if self.current_beat != beat:
            self.current_beat = beat

            if self.current_beat % 4 == 0:
                if measure == 0:
                    self.play_sound("tick", 45, 90)
                else:
                    self.play_sound("tick", 45, 75)
            else:
                self.play_sound("tick", 45, 50)

        if self.current_measure != measure:
            self.current_measure = measure

            # dev, testing chord playback
            current_chord = self.chord_progression[int(self.current_measure % len(self.chord_progression))]
            self.play_chord("guitar", current_chord.get_pitches(), 60)

    def play_sound(self, instrument = "tick", pitch = 45, velocity = 75):
        patch = (128, 0)
        if instrument == "piano":
            patch = (0, 2)
        elif instrument == "drums":
            patch = (128, 8)

        if instrument == "tick":
            if self.previous_note_metro != None:
                for previous_note in self.previous_note_metro:
                    self.metro_synth.noteoff(self.channel, previous_note)
            self.metro_synth.program(self.channel, patch[0], patch[1])
            self.metro_synth.noteon(self.channel, pitch, velocity)
            self.previous_note_metro = [pitch]
        else:
            if self.previous_note != None:
                for previous_note in self.previous_note:
                    self.performance_synth.noteoff(self.channel, previous_note)
            self.performance_synth.program(self.channel, patch[0], patch[1])
            self.performance_synth.noteon(self.channel, pitch, velocity)
            self.previous_note = [pitch]

    def play_chord(self, instrument = "piano", pitches = [], velocity = 80):
        patch = (0, 2)
        if instrument == "clav":
            patch = (0, 7)
        elif instrument == "xylo":
            patch = (0, 13)
        elif instrument == "guitar":
            patch = (0, 26)
        elif instrument == "violin":
            patch = (0, 40)
        elif instrument == "trumpet":
            patch = (0, 56)
        elif instrument == "sax":
            patch = (0, 66)

        if self.previous_note != None:
            for previous_note in self.previous_note:
                self.performance_synth.noteoff(self.channel, previous_note)
        self.performance_synth.program(self.channel, patch[0], patch[1])
        for pitch in pitches:
            self.performance_synth.noteon(self.channel, pitch, velocity)
        self.previous_note = pitches


