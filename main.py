import time
import numpy as np
from tempo_processor import *
from gesture_recognizer import *
from playback import *
from ui import *

from common.core import *
from common.audio import *
from common.synth import *
from common.gfxutil import *
from common.clock import *
from common.metro import *

from kivy.graphics import Color, Line
from kivy.graphics.instructions import InstructionGroup

class MainWidget1(BaseWidget) :
    def __init__(self):
        super(MainWidget1, self).__init__()
        self.channel = 0

        self.audio = Audio(2)
        self.synth = Synth('sfx/FluidR3_GM.sf2')
        self.tempo_map  = SimpleTempoMap(120)
        self.sched = AudioScheduler(self.tempo_map)
        self.audio.set_generator(self.sched)
        self.sched.set_generator(self.synth)
        self.metro = Metronome(self.sched, self.synth)

        self.tempoProcessor = TempoProcessor(self.change_tempo, self.tempo_map)
        # self.gestureRecognizer = GestureRecognizer(self.quantize_time_to_beat, self.play_sound, self.tempoProcessor, self.tempo_map)

        self.previous_note = None
        self.metro.start()

        # user interface objects
        metro_anchor = Obj(CEllipse(cpos=(Window.width*0.5, Window.height*0.25), csize=(Window.width*0.025, Window.width*0.025)), (1.0, 0.0, 0.0))
        self.canvas.add(metro_anchor)
        self.metro_line = SolidLine((Window.width*0.5, Window.height*0.25), (Window.width*0.5, Window.height*0.75), (1.0, 0.0, 0.0), 6.0)
        self.metro_anim_x = 0
        self.canvas.add(self.metro_line)

        self.objects = [metro_anchor, self.metro_line]

    def change_tempo(self, new_tempo):
        print("NEW TEMPO: "+str(new_tempo))

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

    def quantize_time_to_beat(self, time, round_up=True):
        bps = self.tempo_map.bpm/60.0
        beat = int(ceil(time * bps))
        if round_up == False: beat = int(round(time * bps))
        return beat

    def on_update(self) :
        self.audio.on_update()

        dt = kivyClock.frametime
        # self.gestureRecognizer.on_update(dt)
        self.tempoProcessor.on_update(dt)

        # user interface updates

        self.metro_anim_x += dt * (self.tempo_map.bpm * 1.0 / 60.0) * np.pi
        h = Window.height*0.5
        x = (np.sin(self.metro_anim_x + (np.pi*0.5))*Window.width*0.15)
        theta = np.arctan(x/h)
        y = (x / np.sin(theta))-h
        self.metro_line.end = ((Window.width*0.5)+x, (Window.height*0.75)-y)

        for obj in self.objects:
            obj.on_update(dt)

run(MainWidget1)
