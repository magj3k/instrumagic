from math import *
import numpy as np
#from pydub import AudioSegment
#from pydub.playback import play
#from music21 import instrument, midi
#import pygame


class PlaybackSystem(object):
    def __init__(self, t=0):
        self.t = t
        self.beats_per_minute = 120
        self.current_beat = 0
        #pygame.init()
        #pygame.mixer.music.load("test.wav")

    def quantize_time_to_beat(self, time, round_up=True):
        bps = self.beats_per_minute/60.0
        beat = int(ceil(time * bps))
        if round_up == False: beat = int(round(time * bps))
        return beat

    def beat_callback(self, beat):
        if beat % 4 == 0:
            print("BEAT: "+str(beat))
            #pygame.mixer.music.play()



            # guitar = instrument.fromString("Electric Guitar")
            # print(guitar.stringPitches)
            # sp = midi.realtime.StreamPlayer(guitar)
            # sp.play()



            # sfx = AudioSegment.from_wav("./sfx/pop.wav")
            # play(sfx)
        else:
            pass
            # sfx = AudioSegment.from_wav("./sfx/pop2.wav")
            # play(sfx)

    def on_update(self, dt=0.1):
        self.t += dt

        beat = self.quantize_time_to_beat(self.t, False)
        if beat != self.current_beat:
            self.current_beat = beat
            self.beat_callback(self.current_beat)