import customtkinter as ctk
from typing import Callable, Optional
import pyperclip

from config import (
    DEFAULT_WPM, DEFAULT_ERROR_RATE,
    DEFAULT_BURST_SIZE_MAX,
    DEFAULT_THINK_PAUSE_MAX,
    IS_MAC
)

ctk.set_appearance_mode("dark")

class UnifiedWindow(ctk.CTk):
    STATE_IDLE = "idle"
    STATE_EXPANDED = "expanded"
    STATE_TYPING = "typing"
    
    COLLAPSED_WIDTH = 340
    COLLAPSED_HEIGHT = 220
    EXPANDED_WIDTH = 340
    EXPANDED_HEIGHT = 490

    BG_PRIMARY = "#1a1a1a"
    BG_SECONDARY = "#2a2a2a"
    BG_TERTIARY = "#3a3a3a"
    BORDER_COLOR = "#4a4a4a"
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#a0a0a0"
    TEXT_MUTED = "#666666"
    ACCENT = "#10a37f"
    ACCENT_HOVER = "#1db88e"

    def __init__(self, on_start: Optional[Callable] = None,
                 on_pause: Optional[Callable] = None,
                 on_resume: Optional[Callable] = None,
                 on_stop: Optional[Callable] = None):
        super().__init__()
        
        self.on_start = on_start
        self.on_pause = on_pause
        self.on_resume = on_resume
        self.on_stop = on_stop
        
        self._state = self.STATE_IDLE
        self._is_paused = False
        self._clipboard_loaded = False
        
        self.title("TextTyper")
        self.geometry(f"{self.COLLAPSED_WIDTH}x{self.COLLAPSED_HEIGHT}+50+50")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.95)
        self.configure(fg_color=self.BG_PRIMARY)
        
        self.overrideredirect(True)
        
        self._create_widgets()
        self._bind_events()
        self._load_clipboard()
        
        self._keep_on_top()

    def _keep_on_top(self):
        self.attributes("-topmost", True)
        self.lift()
        self.after(100, self._keep_on_top)

    def _create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self._create_header()
        self._create_text_input()
        self._create_settings_section()
        self._create_progress_section()
        self._create_buttons_section()
        
        self._update_visibility()

    def _create_header(self):
        self.header_frame = ctk.CTkFrame(
            self, 
            fg_color=self.BG_SECONDARY, 
            corner_radius=0, 
            height=28
        )
        self.header_frame.grid(row=0, column=0, sticky="ew")
        self.header_frame.grid_propagate(False)
        
        inner_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        inner_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        self.title_label = ctk.CTkLabel(
            inner_frame,
            text="TextTyper",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.TEXT_SECONDARY
        )
        self.title_label.pack(side="left", padx=(0, 8))
        
        self.close_btn = ctk.CTkButton(
            inner_frame,
            text="",
            width=10,
            height=10,
            corner_radius=5,
            fg_color="#ff5f57",
            hover_color="#ff3b30",
            command=self._on_close
        )
        self.close_btn.pack(side="left")

    def _create_text_input(self):
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.grid(row=1, column=0, padx=14, pady=(8, 6), sticky="nsew")
        self.input_frame.grid_columnconfigure(0, weight=1)
        self.input_frame.grid_rowconfigure(0, weight=1)
        
        self.text_input = ctk.CTkTextbox(
            self.input_frame,
            font=ctk.CTkFont(family="SF Mono", size=11),
            fg_color=self.BG_SECONDARY,
            text_color=self.TEXT_PRIMARY,
            border_width=1,
            border_color=self.BORDER_COLOR,
            corner_radius=8,
            height=95,
            wrap="word"
        )
        self.text_input.grid(row=0, column=0, sticky="nsew")
        self.text_input.bind("<KeyRelease>", self._on_text_change)
        self.text_input.bind("<FocusIn>", self._on_text_focus)

    def _create_settings_section(self):
        self.settings_frame = ctk.CTkFrame(
            self, 
            fg_color=self.BG_SECONDARY,
            corner_radius=10,
            border_width=1,
            border_color=self.BORDER_COLOR
        )
        self.settings_frame.grid(row=2, column=0, padx=14, pady=6, sticky="ew")
        self.settings_frame.grid_columnconfigure(1, weight=1)
        
        self._create_slider_row(self.settings_frame, 0, "Speed", 30, 400, DEFAULT_WPM, self._on_wpm_change, " wpm")
        self._create_slider_row(self.settings_frame, 1, "Errors", 0, 10, int(DEFAULT_ERROR_RATE * 100), self._on_error_change, "%")
        self._create_slider_row(self.settings_frame, 2, "Pause", 1, 8, int(DEFAULT_THINK_PAUSE_MAX), self._on_pause_change, "s")
        self._create_slider_row(self.settings_frame, 3, "Burst", 1, 8, DEFAULT_BURST_SIZE_MAX, self._on_burst_change, " sent")

    def _create_slider_row(self, parent, row, label, from_, to, default, command, suffix=""):
        label_widget = ctk.CTkLabel(
            parent,
            text=label,
            font=ctk.CTkFont(size=11),
            text_color=self.TEXT_SECONDARY,
            width=45,
            anchor="w"
        )
        label_widget.grid(row=row, column=0, padx=(10, 6), pady=6, sticky="w")
        
        slider = ctk.CTkSlider(
            parent,
            from_=from_, to=to,
            number_of_steps=to - from_,
            progress_color=self.ACCENT,
            button_color=self.TEXT_PRIMARY,
            button_hover_color=self.ACCENT,
            fg_color=self.BG_TERTIARY,
            height=14
        )
        slider.set(default)
        slider.configure(command=lambda v, c=command, s=suffix: c(v, s))
        slider.grid(row=row, column=1, padx=4, pady=6, sticky="ew")
        
        value_label = ctk.CTkLabel(
            parent,
            text=f"{default}{suffix}",
            font=ctk.CTkFont(size=11),
            text_color=self.ACCENT,
            width=55,
            anchor="e"
        )
        value_label.grid(row=row, column=2, padx=(4, 10), pady=6, sticky="e")
        
        setattr(self, f"{label.lower()}_slider", slider)
        setattr(self, f"{label.lower()}_value", value_label)

    def _create_progress_section(self):
        self.progress_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.progress_frame.grid(row=3, column=0, padx=14, pady=6, sticky="ew")
        self.progress_frame.grid_columnconfigure(0, weight=1)
        
        self.progress_bar = ctk.CTkProgressBar(
            self.progress_frame,
            height=6,
            progress_color=self.ACCENT,
            fg_color=self.BG_TERTIARY,
            corner_radius=3
        )
        self.progress_bar.set(0)
        self.progress_bar.grid(row=0, column=0, sticky="ew")
        
        info_frame = ctk.CTkFrame(self.progress_frame, fg_color="transparent")
        info_frame.grid(row=1, column=0, sticky="ew", pady=(4, 0))
        info_frame.grid_columnconfigure(1, weight=1)
        
        self.progress_percent = ctk.CTkLabel(
            info_frame,
            text="0%",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=self.ACCENT
        )
        self.progress_percent.grid(row=0, column=0, sticky="w")
        
        self.time_remaining = ctk.CTkLabel(
            info_frame,
            text="--:--",
            font=ctk.CTkFont(size=11),
            text_color=self.TEXT_MUTED
        )
        self.time_remaining.grid(row=0, column=2, sticky="e")

    def _create_buttons_section(self):
        self.buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.buttons_frame.grid(row=4, column=0, padx=14, pady=(6, 10), sticky="ew")
        self.buttons_frame.grid_columnconfigure(0, weight=1)
        
        self.start_container = ctk.CTkFrame(self.buttons_frame, fg_color="transparent")
        self.start_container.grid(row=0, column=0, sticky="ew")
        self.start_container.grid_columnconfigure(0, weight=0)
        self.start_container.grid_columnconfigure(1, weight=1)
        
        self.start_btn = ctk.CTkButton(
            self.start_container,
            text="Start",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.ACCENT,
            hover_color=self.ACCENT_HOVER,
            text_color=self.TEXT_PRIMARY,
            corner_radius=8,
            width=90,
            height=44,
            command=self._on_start_click
        )
        self.start_btn.grid(row=0, column=0, rowspan=2, sticky="ns")
        
        self.stats_label = ctk.CTkLabel(
            self.start_container,
            text="0 chars • ~0s",
            font=ctk.CTkFont(size=12),
            text_color=self.TEXT_PRIMARY,
            anchor="e"
        )
        self.stats_label.grid(row=0, column=1, sticky="e", padx=(10, 0), pady=(4, 0))
        
        hotkey_text = "⌘⇧B" if IS_MAC else "Ctrl+Shift+B"
        self.hotkey_label = ctk.CTkLabel(
            self.start_container,
            text=hotkey_text,
            font=ctk.CTkFont(size=9),
            text_color=self.TEXT_MUTED,
            anchor="e"
        )
        self.hotkey_label.grid(row=1, column=1, sticky="e", padx=(10, 0), pady=(0, 4))
        
        self._update_start_button()
        
        self.expand_btn = ctk.CTkButton(
            self.buttons_frame,
            text="▼",
            font=ctk.CTkFont(size=10),
            fg_color="transparent",
            hover_color=self.BG_SECONDARY,
            text_color=self.TEXT_MUTED,
            corner_radius=4,
            width=30,
            height=16,
            command=self._toggle_expand
        )
        self.expand_btn.grid(row=1, column=0, pady=(2, 0))
        
        self.pause_btn = ctk.CTkButton(
            self.buttons_frame,
            text="Pause",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.BG_SECONDARY,
            hover_color=self.BG_TERTIARY,
            text_color=self.TEXT_PRIMARY,
            corner_radius=8,
            height=40,
            border_width=1,
            border_color=self.BORDER_COLOR,
            command=self._on_pause_click
        )
        
        self.stop_btn = ctk.CTkButton(
            self.buttons_frame,
            text="Stop",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#ff5f57",
            hover_color="#ff3b30",
            text_color=self.TEXT_PRIMARY,
            corner_radius=8,
            height=40,
            command=self._on_stop_click
        )

    def _bind_events(self):
        self.header_frame.bind("<Button-1>", self._start_drag)
        self.header_frame.bind("<B1-Motion>", self._on_drag)
        self.title_label.bind("<Button-1>", self._start_drag)
        self.title_label.bind("<B1-Motion>", self._on_drag)

    def _start_drag(self, event):
        self._drag_x = event.x
        self._drag_y = event.y

    def _on_drag(self, event):
        x = self.winfo_x() + event.x - self._drag_x
        y = self.winfo_y() + event.y - self._drag_y
        self.geometry(f"+{x}+{y}")

    def _load_clipboard(self):
        try:
            clipboard = pyperclip.paste()
            if clipboard and clipboard.strip():
                self.text_input.delete("0.0", "end")
                self.text_input.insert("0.0", clipboard)
                self._clipboard_loaded = True
                self._update_start_button()
        except:
            pass

    def _on_text_focus(self, event):
        pass

    def _on_text_change(self, event):
        self._update_start_button()

    def _get_text_content(self):
        return self.text_input.get("0.0", "end-1c")

    def _update_start_button(self):
        text = self._get_text_content()
        
        if text and text.strip():
            from engine.markdown_parser import MarkdownParser
            parser = MarkdownParser()
            char_count = parser.get_plain_text_length(text)
            
            wpm = self.speed_slider.get() if hasattr(self, 'speed_slider') else DEFAULT_WPM
            est_seconds = (char_count / (wpm * 5)) * 60
            
            if est_seconds < 60:
                time_str = f"~{int(est_seconds)}s"
            else:
                time_str = f"~{int(est_seconds // 60)}m {int(est_seconds % 60)}s"
            
            if hasattr(self, 'stats_label'):
                self.stats_label.configure(text=f"{char_count} chars • {time_str}")
        else:
            if hasattr(self, 'stats_label'):
                self.stats_label.configure(text="0 chars • ~0s")

    def _update_visibility(self):
        if self._state == self.STATE_IDLE:
            self.geometry(f"{self.COLLAPSED_WIDTH}x{self.COLLAPSED_HEIGHT}")
            self.input_frame.grid()
            self.settings_frame.grid_remove()
            self.progress_frame.grid_remove()
            self.start_container.grid()
            self.expand_btn.grid()
            self.expand_btn.configure(text="▼")
            self.pause_btn.grid_remove()
            self.stop_btn.grid_remove()
            self._update_start_button()
            
        elif self._state == self.STATE_EXPANDED:
            self.geometry(f"{self.EXPANDED_WIDTH}x{self.EXPANDED_HEIGHT}")
            self.input_frame.grid()
            self.settings_frame.grid()
            self.progress_frame.grid_remove()
            self.start_container.grid()
            self.expand_btn.grid()
            self.expand_btn.configure(text="▲")
            self.pause_btn.grid_remove()
            self.stop_btn.grid_remove()
            
        elif self._state == self.STATE_TYPING:
            self.geometry(f"{self.COLLAPSED_WIDTH}x{self.COLLAPSED_HEIGHT}")
            self.input_frame.grid()
            self.settings_frame.grid_remove()
            self.progress_frame.grid()
            self.start_container.grid_remove()
            self.expand_btn.grid_remove()
            self.buttons_frame.grid_columnconfigure(0, weight=1)
            self.buttons_frame.grid_columnconfigure(1, weight=1)
            self.pause_btn.grid(row=0, column=0, sticky="ew", padx=(0, 4))
            self.stop_btn.grid(row=0, column=1, sticky="ew", padx=(4, 0))

    def _toggle_expand(self):
        if self._state == self.STATE_IDLE:
            self._state = self.STATE_EXPANDED
        else:
            self._state = self.STATE_IDLE
        self._update_visibility()

    def _on_wpm_change(self, value, suffix):
        self.speed_value.configure(text=f"{int(value)}{suffix}")
        self._update_start_button()

    def _on_error_change(self, value, suffix):
        self.errors_value.configure(text=f"{int(value)}{suffix}")

    def _on_pause_change(self, value, suffix):
        self.pause_value.configure(text=f"{int(value)}{suffix}")

    def _on_burst_change(self, value, suffix):
        self.burst_value.configure(text=f"{int(value)}{suffix}")

    def _on_start_click(self):
        text = self._get_text_content()
        if not text or not text.strip():
            self._load_clipboard()
            text = self._get_text_content()
            if not text or not text.strip():
                return
        
        self._state = self.STATE_TYPING
        self._is_paused = False
        self._update_visibility()
        
        if self.on_start:
            settings = self.get_settings()
            self.on_start(text, settings)

    def trigger_start(self):
        self._on_start_click()

    def _on_pause_click(self):
        if self._is_paused:
            self._is_paused = False
            self.pause_btn.configure(text="Pause")
            if self.on_resume:
                self.on_resume()
        else:
            self._is_paused = True
            self.pause_btn.configure(text="Resume")
            if self.on_pause:
                self.on_pause()

    def _on_stop_click(self):
        self._state = self.STATE_IDLE
        self._is_paused = False
        self.pause_btn.configure(text="Pause")
        self.progress_bar.set(0)
        self.buttons_frame.grid_columnconfigure(0, weight=1)
        self.buttons_frame.grid_columnconfigure(1, weight=0)
        self._update_visibility()
        
        if self.on_stop:
            self.on_stop()

    def _on_close(self):
        if self.on_stop:
            self.on_stop()
        self.destroy()

    def get_settings(self):
        burst_max = int(self.burst_slider.get())
        burst_min = max(1, burst_max - 2)
        pause_val = self.pause_slider.get()
        
        return {
            'wpm': int(self.speed_slider.get()),
            'error_rate': self.errors_slider.get() / 100,
            'burst_min': burst_min,
            'burst_max': burst_max,
            'think_pause_min': max(0.5, pause_val - 1.0),
            'think_pause_max': pause_val
        }

    def update_progress(self, current: int, total: int, remaining_seconds: float = 0):
        if total == 0:
            return
        
        progress = current / total
        self.progress_bar.set(progress)
        self.progress_percent.configure(text=f"{int(progress * 100)}%")
        
        if remaining_seconds > 0:
            minutes = int(remaining_seconds // 60)
            seconds = int(remaining_seconds % 60)
            self.time_remaining.configure(text=f"{minutes:02d}:{seconds:02d}")

    def show_countdown(self, seconds: int):
        self.start_btn.configure(text=f"Starting in {seconds}...")

    def on_typing_complete(self):
        self._state = self.STATE_IDLE
        self._is_paused = False
        self.buttons_frame.grid_columnconfigure(0, weight=1)
        self.buttons_frame.grid_columnconfigure(1, weight=0)
        self._update_visibility()

    def set_text(self, text: str):
        self.text_input.delete("0.0", "end")
        self.text_input.insert("0.0", text)
        self._update_start_button()
