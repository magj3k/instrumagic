class PlaybackSystem(object):
    def __init__(self, start_time):
        self.start_time = start_time

    def quantize_time_to_beat(self, time):
        raise NotImplementedError