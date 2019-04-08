from core import *
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line
from kivy.graphics.instructions import InstructionGroup
from kivy.clock import Clock as kivyClock

import numpy as np

class MainWidget(BaseWidget) :
    def __init__(self):
        super(MainWidget, self).__init__()

        # self.canvas.add(self.display)

    def on_update(self) :
        dt = kivyClock.frametime

def launch_ui():
    run(MainWidget, "Automatic Accompaniment")