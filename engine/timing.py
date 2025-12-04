import random
import math
from config import COMMON_BIGRAMS

class TimingEngine:
    def __init__(self, wpm=60, micro_pause_min=0.05, micro_pause_max=0.15,
                 think_pause_min=1.0, think_pause_max=3.0):
        self.wpm = wpm
        self.micro_pause_min = micro_pause_min
        self.micro_pause_max = micro_pause_max
        self.think_pause_min = think_pause_min
        self.think_pause_max = think_pause_max
        self.chars_typed = 0
        self.fatigue_factor = 1.0
        self._burst_speed_multiplier = 1.0
        self._chars_in_current_burst = 0

    def _base_delay(self):
        chars_per_minute = self.wpm * 5
        base = 60.0 / chars_per_minute
        return base

    def _apply_gaussian_variation(self, delay):
        variation = random.gauss(1.0, 0.25)
        return delay * max(0.5, min(2.0, variation))

    def _apply_fatigue(self, delay):
        fatigue_increase = 1.0 + (self.chars_typed / 8000) * 0.08
        self.fatigue_factor = min(1.15, fatigue_increase)
        return delay * self.fatigue_factor

    def start_new_burst(self):
        self._burst_speed_multiplier = random.uniform(0.7, 1.3)
        self._chars_in_current_burst = 0

    def get_keystroke_delay(self, prev_char, current_char):
        base = self._base_delay()
        
        bigram = (prev_char + current_char).lower()
        if bigram in COMMON_BIGRAMS:
            base *= 0.8
        
        if current_char == ' ':
            base *= random.uniform(1.0, 1.4)
        elif current_char == '\n':
            base *= random.uniform(1.2, 1.8)
        elif current_char in '.,':
            base *= random.uniform(0.9, 1.3)
        elif current_char in '!?':
            base *= random.uniform(1.0, 1.5)
        elif current_char in ';:':
            base *= random.uniform(1.1, 1.6)
        elif current_char.isupper():
            base *= random.uniform(1.0, 1.2)
        elif current_char in '0123456789':
            base *= random.uniform(1.0, 1.15)
        elif current_char in '[]{}()<>':
            base *= random.uniform(1.2, 1.5)
        
        base *= self._burst_speed_multiplier
        
        delay = self._apply_gaussian_variation(base)
        delay = self._apply_fatigue(delay)
        
        if random.random() < 0.03:
            delay += random.uniform(0.15, 0.4)
        
        if random.random() < 0.08 and prev_char == ' ':
            delay += random.uniform(0.1, 0.3)
        
        self.chars_typed += 1
        self._chars_in_current_burst += 1
        
        return max(0.008, delay)

    def get_word_pause(self):
        if random.random() < 0.15:
            return random.uniform(0.2, 0.6)
        return 0

    def get_think_pause(self):
        base_pause = random.uniform(self.think_pause_min, self.think_pause_max)
        if random.random() < 0.3:
            base_pause *= random.uniform(1.2, 1.8)
        return base_pause

    def get_error_correction_delay(self):
        return random.uniform(0.08, 0.2)

    def get_formatting_delay(self):
        return random.uniform(0.12, 0.3)

    def estimate_total_time(self, total_chars, error_rate=0.03):
        base_time = (total_chars / (self.wpm * 5)) * 60
        error_overhead = total_chars * error_rate * 0.25
        avg_sentences = total_chars / 80
        think_time = avg_sentences * ((self.think_pause_min + self.think_pause_max) / 2) / 3
        hesitation_overhead = total_chars * 0.03 * 0.25
        return base_time + error_overhead + think_time + hesitation_overhead

    def reset(self):
        self.chars_typed = 0
        self.fatigue_factor = 1.0
        self._burst_speed_multiplier = 1.0
        self._chars_in_current_burst = 0
