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

    def _base_delay(self):
        chars_per_minute = self.wpm * 5
        base = 60.0 / chars_per_minute
        return base

    def _apply_gaussian_variation(self, delay):
        variation = random.gauss(1.0, 0.15)
        return delay * max(0.5, min(1.5, variation))

    def _apply_fatigue(self, delay):
        fatigue_increase = 1.0 + (self.chars_typed / 5000) * 0.1
        self.fatigue_factor = min(1.3, fatigue_increase)
        return delay * self.fatigue_factor

    def get_keystroke_delay(self, prev_char, current_char):
        base = self._base_delay()
        
        bigram = (prev_char + current_char).lower()
        if bigram in COMMON_BIGRAMS:
            base *= 0.7
        
        if current_char in ' \n\t':
            base *= 1.3
        elif current_char in '.,!?;:':
            base *= 1.2
        elif current_char.isupper():
            base *= 1.15
        elif current_char in '0123456789':
            base *= 1.1
        elif current_char in '[]{}()<>':
            base *= 1.4
        
        delay = self._apply_gaussian_variation(base)
        delay = self._apply_fatigue(delay)
        
        noise = random.uniform(self.micro_pause_min, self.micro_pause_max)
        delay += noise * 0.3
        
        self.chars_typed += 1
        return max(0.02, delay)

    def get_think_pause(self):
        return random.uniform(self.think_pause_min, self.think_pause_max)

    def get_error_correction_delay(self):
        return random.uniform(0.1, 0.25)

    def get_formatting_delay(self):
        return random.uniform(0.15, 0.35)

    def estimate_total_time(self, total_chars, error_rate=0.03):
        base_time = (total_chars / (self.wpm * 5)) * 60
        error_overhead = total_chars * error_rate * 0.3
        avg_sentences = total_chars / 80
        think_time = avg_sentences * ((self.think_pause_min + self.think_pause_max) / 2) / 3
        return base_time + error_overhead + think_time

    def reset(self):
        self.chars_typed = 0
        self.fatigue_factor = 1.0

