

class PitchTracker(object):
    def __init__(self):
        self.t = 0

    def audio_input_func(self):
        print("AUDIO INPUT RECEIVED")

    def on_update(self, dt):
        self.t += dt