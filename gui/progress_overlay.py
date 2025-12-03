import customtkinter as ctk
from typing import Callable, Optional

from config import OVERLAY_WIDTH, OVERLAY_HEIGHT

class ProgressOverlay(ctk.CTkToplevel):
    def __init__(self, on_pause: Optional[Callable] = None,
                 on_resume: Optional[Callable] = None,
                 on_cancel: Optional[Callable] = None):
        super().__init__()
        
        self.on_pause = on_pause
        self.on_resume = on_resume
        self.on_cancel = on_cancel
        self._is_paused = False
        
        self.title("")
        self.geometry(f"{OVERLAY_WIDTH}x{OVERLAY_HEIGHT}+20+20")
        self.resizable(False, False)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(fg_color="#1a1a2e")
        
        self._create_widgets()
        self._make_draggable()
        
        self.withdraw()

    def _create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        
        header_frame = ctk.CTkFrame(self, fg_color="#16213e", corner_radius=0, height=30)
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)
        
        title = ctk.CTkLabel(
            header_frame,
            text="TextTyper",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#e94560"
        )
        title.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=1, column=0, padx=15, pady=10, sticky="nsew")
        content_frame.grid_columnconfigure(0, weight=1)
        
        self.progress_bar = ctk.CTkProgressBar(
            content_frame,
            width=OVERLAY_WIDTH - 40,
            height=12,
            progress_color="#e94560",
            fg_color="#0f3460",
            corner_radius=6
        )
        self.progress_bar.set(0)
        self.progress_bar.grid(row=0, column=0, columnspan=2, pady=(0, 8))
        
        self.progress_label = ctk.CTkLabel(
            content_frame,
            text="0%",
            font=ctk.CTkFont(size=11),
            text_color="#eaeaea"
        )
        self.progress_label.grid(row=1, column=0, sticky="w")
        
        self.time_label = ctk.CTkLabel(
            content_frame,
            text="--:--",
            font=ctk.CTkFont(size=11),
            text_color="#a1a1a1"
        )
        self.time_label.grid(row=1, column=1, sticky="e")
        
        button_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        button_frame.grid(row=2, column=0, columnspan=2, pady=(8, 0))
        
        self.pause_button = ctk.CTkButton(
            button_frame,
            text="Pause",
            font=ctk.CTkFont(size=11),
            fg_color="#0f3460",
            hover_color="#16213e",
            corner_radius=15,
            width=80,
            height=28,
            command=self._on_pause_click
        )
        self.pause_button.pack(side="left", padx=5)
        
        self.cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            font=ctk.CTkFont(size=11),
            fg_color="#e94560",
            hover_color="#ff6b6b",
            corner_radius=15,
            width=80,
            height=28,
            command=self._on_cancel_click
        )
        self.cancel_button.pack(side="left", padx=5)

    def _make_draggable(self):
        self._drag_data = {"x": 0, "y": 0}
        self.bind("<Button-1>", self._on_drag_start)
        self.bind("<B1-Motion>", self._on_drag_motion)

    def _on_drag_start(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def _on_drag_motion(self, event):
        x = self.winfo_x() + event.x - self._drag_data["x"]
        y = self.winfo_y() + event.y - self._drag_data["y"]
        self.geometry(f"+{x}+{y}")

    def _on_pause_click(self):
        if self._is_paused:
            self._is_paused = False
            self.pause_button.configure(text="Pause")
            if self.on_resume:
                self.on_resume()
        else:
            self._is_paused = True
            self.pause_button.configure(text="Resume")
            if self.on_pause:
                self.on_pause()

    def _on_cancel_click(self):
        if self.on_cancel:
            self.on_cancel()
        self.hide()

    def update_progress(self, current: int, total: int, remaining_seconds: float = 0):
        if total == 0:
            return
        
        progress = current / total
        self.progress_bar.set(progress)
        self.progress_label.configure(text=f"{int(progress * 100)}%")
        
        if remaining_seconds > 0:
            minutes = int(remaining_seconds // 60)
            seconds = int(remaining_seconds % 60)
            self.time_label.configure(text=f"{minutes:02d}:{seconds:02d}")
        else:
            self.time_label.configure(text="--:--")

    def show_countdown(self, seconds: int):
        self.progress_label.configure(text=f"Starting in {seconds}...")
        self.time_label.configure(text="")
        self.progress_bar.set(0)

    def show(self):
        self._is_paused = False
        self.pause_button.configure(text="Pause")
        self.deiconify()
        self.lift()
        self.attributes("-topmost", True)

    def hide(self):
        self.withdraw()

    def reset(self):
        self._is_paused = False
        self.pause_button.configure(text="Pause")
        self.progress_bar.set(0)
        self.progress_label.configure(text="0%")
        self.time_label.configure(text="--:--")

