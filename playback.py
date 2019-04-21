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
            
    def get_pitches(self, for_feedback):
        pitches = [self.base]
        if for_feedback == True: # plays chords in higher octaves while tracking pitch
            while pitches[0] < 62:
                pitches[0] += 12

        if self.type == "major":
            pitches.append(pitches[0]+4)
            pitches.append(pitches[0]+7)
        elif self.type == "minor":
            pitches.append(pitches[0]+3)
            pitches.append(pitches[0]+7)
        return pitches

class PlaybackSystem(object):
    def __init__(self, audio, tempo_map, tempo_processor, pitch_tracker):
        self.channel = 0

        self.audio = audio
        self.tempo_map = tempo_map
        self.tempo_processor = tempo_processor
        self.pitch_tracker = pitch_tracker

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

        self.chord_progression = [None, None, None, None]
        self.performing = False

    def on_update(self, dt):
        self.t += dt
        self.audio.on_update()

        measure = self.tempo_processor.current_beat(4)
        beat = self.tempo_processor.current_beat()
        if self.current_beat != beat:
            self.current_beat = beat

            if self.current_beat % 4 == 0:
                if measure == 0:
                    vel = 90
                else:
                    vel = 75
            else:
                vel = 50
            if self.performing == True:
                vel = vel * 0.6
            self.play_sound("tick", 45, vel)

        if self.current_measure != measure:
            previous_measure = self.current_measure
            self.current_measure = measure

            # plays back recorded chords during pitch tracking
            if self.pitch_tracker.tracking == True:
                current_chord = self.chord_progression[int(self.current_measure % len(self.chord_progression))]
                if current_chord != None:
                    pitches = current_chord.get_pitches(True)
                    self.play_chord("guitar", pitches, 50)

            # updates chord progression if necessary
            if self.pitch_tracker.tracking == True:
                relevant_pitches = self.pitch_tracker.get_relevant_pitches_and_clear()
                if len(relevant_pitches) > 1:
                    # print("RELEVANT PITCHES: "+str(relevant_pitches))

                    new_chord = Chord(relevant_pitches)
                    self.chord_progression[int(previous_measure % len(self.chord_progression))] = new_chord
                    print("NEW CHORD REGISTERED FOR MEASURE: "+str(previous_measure))

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

    def play_chord_performance(self, instrument = "piano"):
        velocity = 95 # could be tweaked later

        current_chord = self.chord_progression[int(self.current_measure % len(self.chord_progression))]
        if current_chord != None:
            pitches = current_chord.get_pitches(True)
            self.play_chord(instrument, pitches, velocity)


