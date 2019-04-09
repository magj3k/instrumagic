import time
from gesture_recognizer import *
from playback import *
#from ui import *

from common.core import *
from common.audio import *
from common.synth import *
from common.gfxutil import *
from common.clock import *
from common.metro import *

class MainWidget1(BaseWidget) :
    def __init__(self):
        super(MainWidget1, self).__init__()
        self.channel = 0
        self.patch = (128, 0)

        self.audio = Audio(2)
        self.synth = Synth('sfx/FluidR3_GM.sf2')
        self.gestureRecognizer = GestureRecognizer(self.quantize_time_to_beat, self.play_sound)

        self.tempo_map  = SimpleTempoMap(120)
        self.sched = AudioScheduler(self.tempo_map)
        self.audio.set_generator(self.sched)
        self.sched.set_generator(self.synth)
        self.metro = Metronome(self.sched, self.synth)

        self.previous_note = None

    def play_sound(self):
        print("PLAY SOUND")
        if self.previous_note != None: self.synth.noteoff(self.channel, self.previous_note)
        self.synth.program(self.channel, self.patch[0], self.patch[1])

        note = 37
        velocity = 75
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
        self.gestureRecognizer.on_update(dt)

run(MainWidget1)
