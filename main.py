import time
import numpy as np
from tempo_processor import *
# from gesture_recognizer import *
from playback import *
from ui import *

from common.core import *
from common.audio import *
from common.synth import *
from common.gfxutil import *
from common.clock import *
from common.metro import *

from kivy.graphics import Color, Line, Rectangle
from kivy.graphics.instructions import InstructionGroup

class MainWidget1(BaseWidget) :
    def __init__(self):
        super(MainWidget1, self).__init__()
        self.channel = 0

        self.audio = Audio(2)
        self.synth = Synth('sfx/FluidR3_GM.sf2')
        self.tempo_map  = SimpleTempoMap(100)
        self.sched = AudioScheduler(self.tempo_map)
        self.audio.set_generator(self.sched)
        self.sched.set_generator(self.synth)
        self.metro = Metronome(self.sched, self.synth)

        self.tempoProcessor = TempoProcessor(self.change_tempo, self.tempo_map)
        self.playbackSystem = PlaybackSystem(self.synth, self.audio)
        # self.gestureRecognizer = GestureRecognizer(self.quantize_time_to_beat, self.play_sound, self.tempoProcessor, self.tempo_map)

        # user interface objects
        self.metro_offset_y = -Window.height*0.125
        metro_anchor_bg = Obj(CEllipse(cpos=(Window.width*0.5, (Window.height*0.25)+self.metro_offset_y), csize=(Window.width*0.035, Window.width*0.035)), (1.0, 0.0, 0.0))
        self.canvas.add(metro_anchor_bg)
        metro_anchor = Obj(CEllipse(cpos=(Window.width*0.5, (Window.height*0.25)+self.metro_offset_y), csize=(Window.width*0.025, Window.width*0.025)), (1.0, 1.0, 1.0))
        self.canvas.add(metro_anchor)
        self.metro_line = SolidLine((Window.width*0.5, (Window.height*0.25)+self.metro_offset_y), (Window.width*0.5, (Window.height*0.75)+self.metro_offset_y), (1.0, 1.0, 1.0), 6.0)
        self.metro_anim_x = 0
        self.canvas.add(self.metro_line)

        # measure indicators
        measure_indicator_size = (Window.width*0.09, Window.width*0.09)
        self.measure_offset_y = 0
        self.measure_1_indicator = Obj(Rectangle(pos=((Window.width*2.0/7.0) - measure_indicator_size[0]/2, (Window.height*0.825) - measure_indicator_size[1]/2), size=measure_indicator_size), (1.0, 1.0, 1.0), "graphics/beat_1.png")
        self.canvas.add(self.measure_1_indicator)
        self.measure_2_indicator = Obj(Rectangle(pos=((Window.width*3.0/7.0) - measure_indicator_size[0]/2, (Window.height*0.825) - measure_indicator_size[1]/2), size=measure_indicator_size), (1.0, 1.0, 1.0), "graphics/beat_2.png")
        self.canvas.add(self.measure_2_indicator)
        self.measure_3_indicator = Obj(Rectangle(pos=((Window.width*4.0/7.0) - measure_indicator_size[0]/2, (Window.height*0.825) - measure_indicator_size[1]/2), size=measure_indicator_size), (1.0, 1.0, 1.0), "graphics/beat_3.png")
        self.canvas.add(self.measure_3_indicator)
        self.measure_4_indicator = Obj(Rectangle(pos=((Window.width*5.0/7.0) - measure_indicator_size[0]/2, (Window.height*0.825) - measure_indicator_size[1]/2), size=measure_indicator_size), (1.0, 1.0, 1.0), "graphics/beat_4.png")
        self.canvas.add(self.measure_4_indicator)

        self.objects = [metro_anchor, self.metro_line, self.measure_1_indicator, self.measure_2_indicator, self.measure_3_indicator, self.measure_4_indicator]

        self.metro.start()

    def change_tempo(self, new_tempo):
        print("NEW TEMPO: "+str(new_tempo))

    def on_update(self) :
        dt = kivyClock.frametime

        self.playbackSystem.on_update(dt)
        # self.gestureRecognizer.on_update(dt)
        self.tempoProcessor.on_update(dt)

        # metronome interface updates
        self.metro_anim_x += dt * (self.tempo_map.bpm * 1.0 / 60.0) * np.pi
        h = Window.height*0.5
        x = (np.sin(self.metro_anim_x + (np.pi*0.5))*Window.width*0.15)
        theta = np.arctan(x/h)
        y = (x / np.sin(theta))-h
        self.metro_line.end = ((Window.width*0.5)+x, (Window.height*0.75)-y+self.metro_offset_y)

        # beat indicator updates
        current_measure = self.tempoProcessor.current_beat(False)
        if current_measure == 0:
            self.measure_1_indicator.color = Color(0.5, 0.5, 1.0)
        else:
            self.measure_1_indicator.color = Color(0.25, 0.25, 0.25)
        if current_measure == 1:
            self.measure_2_indicator.color = Color(0.5, 0.5, 1.0)
        else:
            self.measure_2_indicator.color = Color(0.25, 0.25, 0.25)
        if current_measure == 2:
            self.measure_3_indicator.color = Color(0.5, 0.5, 1.0)
        else:
            self.measure_3_indicator.color = Color(0.25, 0.25, 0.25)
        if current_measure == 3:
            self.measure_4_indicator.color = Color(0.5, 0.5, 1.0)
        else:
            self.measure_4_indicator.color = Color(0.25, 0.25, 0.25)

        # generic user interface updates
        for obj in self.objects:
            obj.on_update(dt)

run(MainWidget1)
