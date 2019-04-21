from math import *
import numpy as np
import aubio
from collections import Counter

A4 = 440
C0 = A4*pow(2, -4.75)
    
def freq_to_pitch(freq):
    h = round(12*log2(max(freq, 0.00001)/(max(C0, 0.00001))))
    return h

class PitchTracker(object):
    def __init__(self):
        self.t = 0

        self.max_time_range = 0.075 # seconds
        self.samples = [] # list of lists of frames with timestamps
        self.all_frames = [] # concatenated list of tracked frames over time range

        self.current_pitches = []

        self.pDetection = aubio.pitch("default", 1024, 1024, 44100)
        self.pDetection.set_unit("Hz")
        self.pDetection.set_silence(-40)

        self.tracking = False

    def get_relevant_pitches_and_clear(self):
        relevant_pitches = []

        if len(self.current_pitches) > 0:
            
            # gets most common pitches
            common_pitches_and_frequencies = Counter(self.current_pitches).most_common(3)
            sorted_common_pitches_and_frequencies = sorted(common_pitches_and_frequencies)

            # extracts base pitch first
            if len(common_pitches_and_frequencies) > 1:
                base_note = sorted_common_pitches_and_frequencies[0]
                print(sorted_common_pitches_and_frequencies)

                if base_note[1] <= 6:
                    base_note = sorted_common_pitches_and_frequencies[1]
                if base_note[1] > 6:

                    # extracts supporting note
                    best_match = None
                    for pitch_and_freq in common_pitches_and_frequencies:
                        if pitch_and_freq != base_note and pitch_and_freq[1] >= 5:
                            if best_match == None or pitch_and_freq[1] > best_match[1] and (best_match[0] == base_note[0]+3 or best_match[0] == base_note[0]+4):
                                best_match = pitch_and_freq

                    relevant_pitches.append(base_note[0])
                    relevant_pitches.append(best_match[0])

        self.current_pitches = []
        return relevant_pitches

    def audio_input_func(self, frames, num_channels):
        if self.tracking == True:
            deinterlaced_frames = frames[::num_channels]
            self.samples.append( (deinterlaced_frames, self.t) )

            self.current_pitch = None
            self.all_frames = []
            if len(self.samples) > 3:
                while np.absolute(self.samples[0][1]-self.samples[-1][1]) > self.max_time_range:
                    self.samples = self.samples[1:]

                for sample in self.samples:
                    self.all_frames.extend(sample[0])

                avg_volume = np.mean(np.absolute(self.all_frames))
                if avg_volume > 0.05: # tracks current pitch if volume is loud enough

                    aubio_samples = np.array(self.all_frames[-1024:], dtype=aubio.float_type)
                    if len(aubio_samples) >= 1024:
                        freq = self.pDetection(aubio_samples)[0]
                        pitch = freq_to_pitch(freq)
                        self.current_pitches.append(pitch)

                        # print("PITCH:" + str(pitch))

    def on_update(self, dt):
        self.t += dt

