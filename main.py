import time
import numpy as np
from tempo_processor import *
# from gesture_recognizer import *
from playback import *
from pitch_tracker import *
from ui import *

from common.core import *
from common.audio import *
from common.synth import *
from common.gfxutil import *
from common.clock import *

from kivy.graphics import Color, Line, Rectangle
from kivy.graphics.instructions import InstructionGroup

class MainWidget1(BaseWidget) :
    def __init__(self):
        super(MainWidget1, self).__init__()

        self.phase = 0 # 0=tempo tracking, 1=pitch tracking, 2=performance

        self.pitchTracker = PitchTracker()
        self.audio = Audio(2, None, self.pitchTracker.audio_input_func)
        self.tempo_map  = SimpleTempoMap(100)

        self.tempoProcessor = TempoProcessor(self.change_tempo, self.tempo_map)
        self.playbackSystem = PlaybackSystem(self.audio, self.tempo_map, self.tempoProcessor, self.pitchTracker)
        # self.gestureRecognizer = GestureRecognizer(self.quantize_time_to_beat, self.play_sound, self.tempoProcessor, self.tempo_map)

        # user interface objects
        self.metro_offset_y = -Window.height*0.135
        metro_anchor_bg = Obj(CEllipse(cpos=(Window.width*0.5, (Window.height*0.25)+self.metro_offset_y), csize=(Window.width*0.035, Window.width*0.035)), (1.0, 0.0, 0.0))
        self.canvas.add(metro_anchor_bg)
        metro_anchor = Obj(CEllipse(cpos=(Window.width*0.5, (Window.height*0.25)+self.metro_offset_y), csize=(Window.width*0.025, Window.width*0.025)), (1.0, 1.0, 1.0))
        self.canvas.add(metro_anchor)
        self.metro_line = SolidLine((Window.width*0.5, (Window.height*0.25)+self.metro_offset_y), (Window.width*0.5, (Window.height*0.75)+self.metro_offset_y), (1.0, 1.0, 1.0), 6.0)
        self.metro_anim_x = 0
        self.canvas.add(self.metro_line)

        # measure indicators
        measure_indicator_size = (Window.width*0.09, Window.width*0.09)
        self.measure_offset_y = -Window.height*0.145
        self.measure_1_indicator = Obj(Rectangle(pos=((Window.width*2.0/7.0) - measure_indicator_size[0]/2, (Window.height*0.825) + self.measure_offset_y - measure_indicator_size[1]/2), size=measure_indicator_size), (1.0, 1.0, 1.0), "graphics/beat_1.png")
        self.canvas.add(self.measure_1_indicator)
        self.measure_2_indicator = Obj(Rectangle(pos=((Window.width*3.0/7.0) - measure_indicator_size[0]/2, (Window.height*0.825) + self.measure_offset_y - measure_indicator_size[1]/2), size=measure_indicator_size), (1.0, 1.0, 1.0), "graphics/beat_2.png")
        self.canvas.add(self.measure_2_indicator)
        self.measure_3_indicator = Obj(Rectangle(pos=((Window.width*4.0/7.0) - measure_indicator_size[0]/2, (Window.height*0.825) + self.measure_offset_y - measure_indicator_size[1]/2), size=measure_indicator_size), (1.0, 1.0, 1.0), "graphics/beat_3.png")
        self.canvas.add(self.measure_3_indicator)
        self.measure_4_indicator = Obj(Rectangle(pos=((Window.width*5.0/7.0) - measure_indicator_size[0]/2, (Window.height*0.825) + self.measure_offset_y - measure_indicator_size[1]/2), size=measure_indicator_size), (1.0, 1.0, 1.0), "graphics/beat_4.png")
        self.canvas.add(self.measure_4_indicator)
        self.measure_indicators = [self.measure_1_indicator, self.measure_2_indicator, self.measure_3_indicator, self.measure_4_indicator]

        # phase indicator
        indicator_size = (Window.width*0.5, Window.width*0.5*117.0/853.0)
        self.phase_indicator = Obj(Rectangle(pos=((Window.width*0.5) - indicator_size[0]/2, (Window.height*0.865) - indicator_size[1]/2), size=indicator_size), (1.0, 1.0, 1.0), "graphics/signal_phase_1.png")
        self.phase_ind_anim_x = 100
        self.canvas.add(self.phase_indicator)

        self.objects = [self.phase_indicator, metro_anchor, self.metro_line, self.measure_1_indicator, self.measure_2_indicator, self.measure_3_indicator, self.measure_4_indicator]

    def on_key_down(self, keycode, modifiers):
        print("Key pressed: "+str(keycode))
        if keycode[0] != 27: # excluding escape key
            self.change_phase((self.phase+1) % 3)

    def change_phase(self, new_phase):
        if self.phase != new_phase:
            self.phase = new_phase
            self.phase_ind_anim_x = 0

            if self.phase == 1:
                self.pitchTracker.tracking = True
            else:
                self.pitchTracker.tracking = False

            if self.phase == 2:
                self.playbackSystem.performing = True
            else:
                self.playbackSystem.performing = False

    def change_tempo(self, new_tempo):
        print("NEW TEMPO: "+str(new_tempo))

    def on_update(self) :
        dt = kivyClock.frametime
        self.phase_ind_anim_x = min(self.phase_ind_anim_x+dt, 100)

        self.pitchTracker.on_update(dt)
        self.playbackSystem.on_update(dt)
        # self.gestureRecognizer.on_update(dt)
        self.tempoProcessor.on_update(dt)

        # metronome interface updates
        self.metro_anim_x += dt * (self.tempo_map.bpm * 1.0 / 60.0) * np.pi
        h = Window.height*0.4
        x = (np.sin(self.metro_anim_x + (np.pi*0.5))*Window.width*0.15)
        theta = np.arctan(x/h)
        y = (x / np.sin(theta))-h
        self.metro_line.end = ((Window.width*0.5)+x, (Window.height*0.65)-y+self.metro_offset_y)

        # beat indicator updates
        current_measure = self.tempoProcessor.current_beat(4)
        for i in range(len(self.measure_indicators)):
            indicator = self.measure_indicators[i]

            if current_measure == i:
                indicator.color.r = 0.5
                indicator.color.g = 0.5
                indicator.color.b = 1.0
            elif self.playbackSystem.chord_progression[i] != None:
                indicator.color.r = 0.15
                indicator.color.g = 0.5
                indicator.color.b = 0.15
            else:
                indicator.color.r = 0.25
                indicator.color.g = 0.25
                indicator.color.b = 0.25

        # phase indicator updates
        if self.phase_ind_anim_x < 1.1:
            self.phase_indicator.color.r = 0.75+(np.cos(self.phase_ind_anim_x*4*(2.0*3.14159)/1.1)*0.25)
            self.phase_indicator.color.g = 0.75+(np.cos(self.phase_ind_anim_x*4*(2.0*3.14159)/1.1)*0.25)
        else:
            self.phase_indicator.color.r = 1.0
            self.phase_indicator.color.g = 1.0

        if self.phase == 0:
            self.phase_indicator.change_texture("graphics/signal_phase_1.png")
        elif self.phase == 1:
            self.phase_indicator.change_texture("graphics/signal_phase_2.png")
        elif self.phase == 2:
            self.phase_indicator.change_texture("graphics/signal_phase_3.png")

        # generic user interface updates
        for obj in self.objects:
            obj.on_update(dt)

run(MainWidget1)
