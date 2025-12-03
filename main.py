import sys
import time
import threading
from pynput import keyboard

from config import HOTKEY_COMBO, COUNTDOWN_SECONDS
from gui.main_window import MainWindow
from gui.progress_overlay import ProgressOverlay
from engine.typer import Typer

class TextTyperApp:
    def __init__(self):
        self.typer = None
        self.typing_thread = None
        self.total_chars = 0
        self.start_time = 0
        
        self.main_window = MainWindow(on_start=self._on_start_typing)
        self.overlay = ProgressOverlay(
            on_pause=self._on_pause,
            on_resume=self._on_resume,
            on_cancel=self._on_cancel
        )
        
        self._setup_hotkey()

    def _setup_hotkey(self):
        self.hotkey_listener = keyboard.GlobalHotKeys({
            HOTKEY_COMBO: self._toggle_window
        })
        self.hotkey_listener.start()

    def _toggle_window(self):
        self.main_window.after(0, self.main_window.toggle_visibility)

    def _on_start_typing(self, text, settings):
        self.main_window.hide()
        
        self.typer = Typer(
            wpm=settings['wpm'],
            error_rate=settings['error_rate'],
            burst_min=settings['burst_min'],
            burst_max=settings['burst_max'],
            think_pause_min=settings['think_pause_min'],
            think_pause_max=settings['think_pause_max']
        )
        self.typer.on_progress = self._on_typing_progress
        self.typer.on_complete = self._on_typing_complete
        
        from engine.markdown_parser import MarkdownParser
        parser = MarkdownParser()
        self.total_chars = parser.get_plain_text_length(text)
        self.estimated_time = self.typer.estimate_time(text)
        
        self.overlay.show()
        self._run_countdown(text)

    def _run_countdown(self, text):
        def countdown():
            for i in range(COUNTDOWN_SECONDS, 0, -1):
                self.overlay.after(0, lambda s=i: self.overlay.show_countdown(s))
                time.sleep(1)
            
            self.start_time = time.time()
            self.overlay.after(0, lambda: self.overlay.update_progress(0, self.total_chars, self.estimated_time))
            
            self.typing_thread = threading.Thread(target=self.typer.type_markdown, args=(text,))
            self.typing_thread.start()
        
        threading.Thread(target=countdown, daemon=True).start()

    def _on_typing_progress(self, current, total):
        elapsed = time.time() - self.start_time
        if current > 0:
            rate = current / elapsed
            remaining = (total - current) / rate if rate > 0 else 0
        else:
            remaining = self.estimated_time
        
        self.overlay.after(0, lambda: self.overlay.update_progress(current, total, remaining))

    def _on_typing_complete(self):
        self.overlay.after(0, self.overlay.hide)
        self.main_window.after(0, self.main_window.show)

    def _on_pause(self):
        if self.typer:
            self.typer.pause()
        self.main_window.after(0, self.main_window.show)

    def _on_resume(self):
        if self.typer:
            self.typer.resume()
        self.main_window.after(0, self.main_window.hide)

    def _on_cancel(self):
        if self.typer:
            self.typer.cancel()
        self.overlay.hide()
        self.main_window.after(0, self.main_window.show)

    def run(self):
        self.main_window.mainloop()

    def cleanup(self):
        self.hotkey_listener.stop()
        if self.typer:
            self.typer.cancel()

def main():
    app = TextTyperApp()
    try:
        app.run()
    except KeyboardInterrupt:
        pass
    finally:
        app.cleanup()

if __name__ == "__main__":
    main()

