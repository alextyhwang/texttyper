import platform

IS_MAC = platform.system() == "Darwin"
MODIFIER_KEY = "cmd" if IS_MAC else "ctrl"

DEFAULT_WPM = 60
DEFAULT_ERROR_RATE = 0.03
DEFAULT_BURST_SIZE_MIN = 2
DEFAULT_BURST_SIZE_MAX = 4
DEFAULT_THINK_PAUSE_MIN = 1.0
DEFAULT_THINK_PAUSE_MAX = 3.0
DEFAULT_MICRO_PAUSE_MIN = 0.05
DEFAULT_MICRO_PAUSE_MAX = 0.15

HOTKEY_COMBO = "<cmd>+<shift>+b" if IS_MAC else "<ctrl>+<shift>+b"

COMMON_BIGRAMS = {
    "th", "he", "in", "er", "an", "re", "on", "at", "en", "nd",
    "ti", "es", "or", "te", "of", "ed", "is", "it", "al", "ar",
    "st", "to", "nt", "ng", "se", "ha", "as", "ou", "io", "le",
    "ve", "co", "me", "de", "hi", "ri", "ro", "ic", "ne", "ea",
    "ra", "ce", "li", "ch", "ll", "be", "ma", "si", "om", "ur"
}

KEYBOARD_ADJACENT = {
    'q': ['w', 'a'], 'w': ['q', 'e', 's', 'a'], 'e': ['w', 'r', 'd', 's'],
    'r': ['e', 't', 'f', 'd'], 't': ['r', 'y', 'g', 'f'], 'y': ['t', 'u', 'h', 'g'],
    'u': ['y', 'i', 'j', 'h'], 'i': ['u', 'o', 'k', 'j'], 'o': ['i', 'p', 'l', 'k'],
    'p': ['o', 'l'],
    'a': ['q', 'w', 's', 'z'], 's': ['a', 'w', 'e', 'd', 'z', 'x'],
    'd': ['s', 'e', 'r', 'f', 'x', 'c'], 'f': ['d', 'r', 't', 'g', 'c', 'v'],
    'g': ['f', 't', 'y', 'h', 'v', 'b'], 'h': ['g', 'y', 'u', 'j', 'b', 'n'],
    'j': ['h', 'u', 'i', 'k', 'n', 'm'], 'k': ['j', 'i', 'o', 'l', 'm'],
    'l': ['k', 'o', 'p'],
    'z': ['a', 's', 'x'], 'x': ['z', 's', 'd', 'c'], 'c': ['x', 'd', 'f', 'v'],
    'v': ['c', 'f', 'g', 'b'], 'b': ['v', 'g', 'h', 'n'], 'n': ['b', 'h', 'j', 'm'],
    'm': ['n', 'j', 'k']
}

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 500
OVERLAY_WIDTH = 300
OVERLAY_HEIGHT = 120

COUNTDOWN_SECONDS = 3

