import random
import time
import threading
from typing import Callable, Optional
from pynput.keyboard import Key, Controller

from config import IS_MAC, KEYBOARD_ADJACENT
from engine.timing import TimingEngine
from engine.markdown_parser import MarkdownParser, InstructionType

class Typer:
    def __init__(self, wpm=60, error_rate=0.03, burst_min=2, burst_max=4,
                 think_pause_min=1.0, think_pause_max=3.0):
        self.keyboard = Controller()
        self.timing = TimingEngine(
            wpm=wpm,
            think_pause_min=think_pause_min,
            think_pause_max=think_pause_max
        )
        self.parser = MarkdownParser()
        self.error_rate = error_rate
        self.burst_min = burst_min
        self.burst_max = burst_max
        
        self._paused = False
        self._cancelled = False
        self._lock = threading.Lock()
        
        self.on_progress: Optional[Callable[[int, int], None]] = None
        self.on_complete: Optional[Callable[[], None]] = None

    def _modifier_key(self):
        return Key.cmd if IS_MAC else Key.ctrl

    def _press_shortcut(self, *keys):
        time.sleep(self.timing.get_formatting_delay())
        for key in keys:
            self.keyboard.press(key)
        for key in reversed(keys):
            self.keyboard.release(key)
        time.sleep(self.timing.get_formatting_delay())

    def _toggle_bold(self):
        self._press_shortcut(self._modifier_key(), 'b')

    def _toggle_italic(self):
        self._press_shortcut(self._modifier_key(), 'i')

    def _apply_heading_size(self, level):
        decrease_times = 4 - level
        for _ in range(decrease_times):
            self._press_shortcut(self._modifier_key(), Key.shift, '.')
            time.sleep(0.1)

    def _get_adjacent_key(self, char):
        lower = char.lower()
        if lower in KEYBOARD_ADJACENT:
            adjacent = random.choice(KEYBOARD_ADJACENT[lower])
            return adjacent.upper() if char.isupper() else adjacent
        return char

    def _type_with_possible_error(self, char, prev_char):
        if char.isalpha() and random.random() < self.error_rate:
            wrong_char = self._get_adjacent_key(char)
            self.keyboard.type(wrong_char)
            time.sleep(self.timing.get_error_correction_delay())
            self.keyboard.press(Key.backspace)
            self.keyboard.release(Key.backspace)
            time.sleep(self.timing.get_error_correction_delay())
        
        self.keyboard.type(char)
        delay = self.timing.get_keystroke_delay(prev_char, char)
        time.sleep(delay)

    def _check_pause(self):
        while self._paused and not self._cancelled:
            time.sleep(0.1)
        return not self._cancelled

    def _should_burst_pause(self, text_so_far):
        sentence_enders = '.!?'
        count = sum(1 for c in text_so_far if c in sentence_enders)
        if not hasattr(self, '_last_burst_count'):
            self._last_burst_count = 0
            self._next_burst_at = random.randint(self.burst_min, self.burst_max)
        
        if count >= self._last_burst_count + self._next_burst_at:
            self._last_burst_count = count
            self._next_burst_at = random.randint(self.burst_min, self.burst_max)
            return True
        return False

    def type_markdown(self, markdown_text: str):
        self._paused = False
        self._cancelled = False
        self._last_burst_count = 0
        self._next_burst_at = random.randint(self.burst_min, self.burst_max)
        self.timing.reset()
        self.timing.start_new_burst()
        
        instructions = self.parser.parse(markdown_text)
        total_chars = self.parser.get_plain_text_length(markdown_text)
        chars_typed = 0
        prev_char = ''
        typed_text = ''
        
        for instruction in instructions:
            if not self._check_pause():
                return
            
            if instruction.type == InstructionType.TEXT:
                for char in instruction.content:
                    if not self._check_pause():
                        return
                    
                    if prev_char == ' ':
                        word_pause = self.timing.get_word_pause()
                        if word_pause > 0:
                            time.sleep(word_pause)
                    
                    self._type_with_possible_error(char, prev_char)
                    prev_char = char
                    typed_text += char
                    chars_typed += 1
                    
                    if self.on_progress:
                        self.on_progress(chars_typed, total_chars)
                    
                    if self._should_burst_pause(typed_text):
                        pause_time = self.timing.get_think_pause()
                        time.sleep(pause_time)
                        self.timing.start_new_burst()
            
            elif instruction.type == InstructionType.BOLD_START:
                self._toggle_bold()
            elif instruction.type == InstructionType.BOLD_END:
                self._toggle_bold()
            elif instruction.type == InstructionType.ITALIC_START:
                self._toggle_italic()
            elif instruction.type == InstructionType.ITALIC_END:
                self._toggle_italic()
            elif instruction.type == InstructionType.HEADING_START:
                self._apply_heading_size(instruction.heading_level)
            elif instruction.type == InstructionType.HEADING_END:
                pass
            elif instruction.type == InstructionType.NEWLINE:
                if not self._check_pause():
                    return
                self.keyboard.press(Key.enter)
                self.keyboard.release(Key.enter)
                chars_typed += 1
                prev_char = '\n'
                typed_text += '\n'
                time.sleep(self.timing.get_keystroke_delay('\n', '\n'))
                if self.on_progress:
                    self.on_progress(chars_typed, total_chars)
        
        if self.on_complete:
            self.on_complete()

    def pause(self):
        with self._lock:
            self._paused = True

    def resume(self):
        with self._lock:
            self._paused = False

    def cancel(self):
        with self._lock:
            self._cancelled = True
            self._paused = False

    def is_paused(self):
        return self._paused

    def estimate_time(self, markdown_text: str):
        total_chars = self.parser.get_plain_text_length(markdown_text)
        return self.timing.estimate_total_time(total_chars, self.error_rate)

