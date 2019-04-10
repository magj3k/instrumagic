import numpy as np

class TempoProcessor(object):
    def __init__(self, change_tempo_func):
        self.previous_up_conducts = [] # as timestamps
        self.previous_down_conducts = [] # as timestamps

        self.clear_threshold = 6.0 # in seconds
        self.change_tempo_func = change_tempo_func

    def strong_sample_size(self):
        return len(self.previous_down_conducts) + (len(self.previous_down_conducts) * 0.5)

    def add_sample(self, timestamp, up_or_down):
        if up_or_down == "up":
            if len(self.previous_up_conducts) > 0 and np.abs(timestamp - self.previous_up_conducts[-1]) > self.clear_threshold:
                self.previous_up_conducts = [timestamp]
            else:
                self.previous_up_conducts.append(timestamp)
        elif up_or_down == "down":
            if len(self.previous_down_conducts) > 0 and np.abs(timestamp - self.previous_down_conducts[-1]) > self.clear_threshold:
                self.previous_down_conducts = [timestamp]
            else:
                self.previous_down_conducts.append(timestamp)

    def estimate_tempo(self, reference_tempo):
        sample_size = self.strong_sample_size()
        if sample_size < 3:
            return None

        time_diff_sum_down = 0
        time_diff_count_down = 0
        time_diff_sum_up = 0
        time_diff_count_up = 0

        # use captured downbeats to capture tempo
        for j in range(len(self.previous_down_conducts)-1):
            i = len(self.previous_down_conducts)-1-j

            down_timestamp = self.previous_down_conducts[i]
            earlier_down_timestamp = self.previous_down_conducts[i-1]

            diff = np.abs(earlier_down_timestamp - down_timestamp)
            time_diff_count_down += 1
            time_diff_sum_down += diff

        # use captured upbeats to influence tempo
        for j in range(len(self.previous_up_conducts)-1):
            i = len(self.previous_up_conducts)-1-j

            up_timestamp = self.previous_up_conducts[i]
            earlier_up_timestamp = self.previous_up_conducts[i-1]

            diff = np.abs(earlier_up_timestamp - up_timestamp)
            time_diff_count_up += 1
            time_diff_sum_up += diff

        if time_diff_count_down == 0 and time_diff_count_up == 0:
            return None

        time_diff_sum_down = time_diff_sum_down/max(time_diff_count_down, 0.0001)
        time_diff_sum_up = time_diff_sum_up/max(time_diff_count_up, 0.0001)

        time_diff_avg = (time_diff_sum_down + time_diff_sum_down + time_diff_sum_up) / 3
        if time_diff_sum_down == 0 and time_diff_sum_up != 0:
            time_diff_avg = time_diff_sum_up
        elif time_diff_sum_up == 0 and time_diff_sum_down != 0:
            time_diff_avg = time_diff_sum_down
        elif time_diff_sum_up == 0 and time_diff_sum_down == 0:
            return None

        suggested_tempo = time_diff_avg * 60.0

        return (suggested_tempo * 0.65) + (reference_tempo * 0.35)

