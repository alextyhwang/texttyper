import customtkinter as ctk
from typing import Callable, Optional

from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT,
    DEFAULT_WPM, DEFAULT_ERROR_RATE,
    DEFAULT_BURST_SIZE_MIN, DEFAULT_BURST_SIZE_MAX,
    DEFAULT_THINK_PAUSE_MIN, DEFAULT_THINK_PAUSE_MAX
)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class MainWindow(ctk.CTk):
    def __init__(self, on_start: Optional[Callable] = None):
        super().__init__()
        
        self.on_start = on_start
        self._visible = False
        
        self.title("TextTyper")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.resizable(False, False)
        
        self.configure(fg_color="#1a1a2e")
        
        self._create_widgets()
        self._bind_events()
        
        self.withdraw()

    def _create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        header = ctk.CTkLabel(
            self,
            text="TextTyper",
            font=ctk.CTkFont(family="SF Pro Display", size=28, weight="bold"),
            text_color="#e94560"
        )
        header.grid(row=0, column=0, pady=(20, 10))
        
        text_frame = ctk.CTkFrame(self, fg_color="#16213e", corner_radius=12)
        text_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        text_frame.grid_columnconfigure(0, weight=1)
        text_frame.grid_rowconfigure(0, weight=1)
        
        self.text_input = ctk.CTkTextbox(
            text_frame,
            font=ctk.CTkFont(family="JetBrains Mono", size=14),
            fg_color="#0f3460",
            text_color="#eaeaea",
            border_width=0,
            corner_radius=8
        )
        self.text_input.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.text_input.insert("0.0", "Paste your markdown text here...")
        
        settings_frame = ctk.CTkFrame(self, fg_color="#16213e", corner_radius=12)
        settings_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        settings_frame.grid_columnconfigure((0, 1), weight=1)
        
        wpm_label = ctk.CTkLabel(
            settings_frame,
            text="WPM",
            font=ctk.CTkFont(size=12),
            text_color="#a1a1a1"
        )
        wpm_label.grid(row=0, column=0, padx=(15, 5), pady=(10, 0), sticky="w")
        
        self.wpm_value_label = ctk.CTkLabel(
            settings_frame,
            text=str(DEFAULT_WPM),
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#e94560"
        )
        self.wpm_value_label.grid(row=0, column=0, padx=(15, 15), pady=(10, 0), sticky="e")
        
        self.wpm_slider = ctk.CTkSlider(
            settings_frame,
            from_=30, to=400,
            number_of_steps=370,
            progress_color="#e94560",
            button_color="#e94560",
            button_hover_color="#ff6b6b",
            command=self._on_wpm_change
        )
        self.wpm_slider.set(DEFAULT_WPM)
        self.wpm_slider.grid(row=1, column=0, padx=15, pady=(5, 10), sticky="ew")
        
        error_label = ctk.CTkLabel(
            settings_frame,
            text="Error Rate",
            font=ctk.CTkFont(size=12),
            text_color="#a1a1a1"
        )
        error_label.grid(row=0, column=1, padx=(5, 15), pady=(10, 0), sticky="w")
        
        self.error_value_label = ctk.CTkLabel(
            settings_frame,
            text=f"{int(DEFAULT_ERROR_RATE * 100)}%",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#e94560"
        )
        self.error_value_label.grid(row=0, column=1, padx=(5, 15), pady=(10, 0), sticky="e")
        
        self.error_slider = ctk.CTkSlider(
            settings_frame,
            from_=0, to=0.1,
            number_of_steps=100,
            progress_color="#e94560",
            button_color="#e94560",
            button_hover_color="#ff6b6b",
            command=self._on_error_change
        )
        self.error_slider.set(DEFAULT_ERROR_RATE)
        self.error_slider.grid(row=1, column=1, padx=15, pady=(5, 10), sticky="ew")
        
        pause_label = ctk.CTkLabel(
            settings_frame,
            text="Think Pause (s)",
            font=ctk.CTkFont(size=12),
            text_color="#a1a1a1"
        )
        pause_label.grid(row=2, column=0, padx=(15, 5), pady=(10, 0), sticky="w")
        
        self.pause_value_label = ctk.CTkLabel(
            settings_frame,
            text=f"{DEFAULT_THINK_PAUSE_MIN}-{DEFAULT_THINK_PAUSE_MAX}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#e94560"
        )
        self.pause_value_label.grid(row=2, column=0, padx=(15, 15), pady=(10, 0), sticky="e")
        
        self.pause_slider = ctk.CTkSlider(
            settings_frame,
            from_=0.5, to=5.0,
            number_of_steps=45,
            progress_color="#e94560",
            button_color="#e94560",
            button_hover_color="#ff6b6b",
            command=self._on_pause_change
        )
        self.pause_slider.set(DEFAULT_THINK_PAUSE_MAX)
        self.pause_slider.grid(row=3, column=0, padx=15, pady=(5, 15), sticky="ew")
        
        burst_label = ctk.CTkLabel(
            settings_frame,
            text="Burst Size (sentences)",
            font=ctk.CTkFont(size=12),
            text_color="#a1a1a1"
        )
        burst_label.grid(row=2, column=1, padx=(5, 15), pady=(10, 0), sticky="w")
        
        self.burst_value_label = ctk.CTkLabel(
            settings_frame,
            text=f"{DEFAULT_BURST_SIZE_MIN}-{DEFAULT_BURST_SIZE_MAX}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#e94560"
        )
        self.burst_value_label.grid(row=2, column=1, padx=(5, 15), pady=(10, 0), sticky="e")
        
        self.burst_slider = ctk.CTkSlider(
            settings_frame,
            from_=1, to=8,
            number_of_steps=7,
            progress_color="#e94560",
            button_color="#e94560",
            button_hover_color="#ff6b6b",
            command=self._on_burst_change
        )
        self.burst_slider.set(DEFAULT_BURST_SIZE_MAX)
        self.burst_slider.grid(row=3, column=1, padx=15, pady=(5, 15), sticky="ew")
        
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=3, column=0, pady=(10, 20))
        
        self.estimate_label = ctk.CTkLabel(
            button_frame,
            text="",
            font=ctk.CTkFont(size=13),
            text_color="#a1a1a1"
        )
        self.estimate_label.pack(pady=(0, 10))
        
        self.start_button = ctk.CTkButton(
            button_frame,
            text="Start Typing",
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#e94560",
            hover_color="#ff6b6b",
            corner_radius=25,
            width=200,
            height=45,
            command=self._on_start_click
        )
        self.start_button.pack()

    def _bind_events(self):
        self.text_input.bind("<FocusIn>", self._on_text_focus)
        self.text_input.bind("<KeyRelease>", self._on_text_change)
        self.bind("<Return>", lambda e: self._on_start_click())
        self.protocol("WM_DELETE_WINDOW", self.toggle_visibility)

    def _on_text_focus(self, event):
        current = self.text_input.get("0.0", "end-1c")
        if current == "Paste your markdown text here...":
            self.text_input.delete("0.0", "end")

    def _on_text_change(self, event):
        self._update_estimate()

    def _on_wpm_change(self, value):
        self.wpm_value_label.configure(text=str(int(value)))
        self._update_estimate()

    def _on_error_change(self, value):
        self.error_value_label.configure(text=f"{int(value * 100)}%")
        self._update_estimate()

    def _on_pause_change(self, value):
        min_val = max(0.5, value - 1.0)
        self.pause_value_label.configure(text=f"{min_val:.1f}-{value:.1f}")

    def _on_burst_change(self, value):
        max_val = int(value)
        min_val = max(1, max_val - 2)
        self.burst_value_label.configure(text=f"{min_val}-{max_val}")

    def _update_estimate(self):
        text = self.get_text()
        if not text or text == "Paste your markdown text here...":
            self.estimate_label.configure(text="")
            return
        
        from engine.markdown_parser import MarkdownParser
        from engine.timing import TimingEngine
        
        parser = MarkdownParser()
        timing = TimingEngine(wpm=int(self.wpm_slider.get()))
        
        char_count = parser.get_plain_text_length(text)
        est_seconds = timing.estimate_total_time(char_count, self.error_slider.get())
        
        if est_seconds < 60:
            time_str = f"{int(est_seconds)} seconds"
        else:
            minutes = int(est_seconds // 60)
            seconds = int(est_seconds % 60)
            time_str = f"{minutes}m {seconds}s"
        
        self.estimate_label.configure(text=f"Estimated time: {time_str}")

    def _on_start_click(self):
        text = self.get_text()
        if not text or text == "Paste your markdown text here...":
            return
        
        if self.on_start:
            settings = self.get_settings()
            self.on_start(text, settings)

    def get_text(self):
        return self.text_input.get("0.0", "end-1c")

    def get_settings(self):
        burst_max = int(self.burst_slider.get())
        burst_min = max(1, burst_max - 2)
        pause_max = self.pause_slider.get()
        pause_min = max(0.5, pause_max - 1.0)
        
        return {
            'wpm': int(self.wpm_slider.get()),
            'error_rate': self.error_slider.get(),
            'burst_min': burst_min,
            'burst_max': burst_max,
            'think_pause_min': pause_min,
            'think_pause_max': pause_max
        }

    def toggle_visibility(self):
        if self._visible:
            self.withdraw()
            self._visible = False
        else:
            self.deiconify()
            self.lift()
            self.focus_force()
            self._visible = True

    def show(self):
        self.deiconify()
        self.lift()
        self.focus_force()
        self._visible = True

    def hide(self):
        self.withdraw()
        self._visible = False

