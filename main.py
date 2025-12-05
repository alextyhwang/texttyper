import sys
import time
import threading
import subprocess
import platform
import os

if platform.system() == "Darwin":
    try:
        from ApplicationServices import AXIsProcessTrusted
    except ImportError:
        AXIsProcessTrusted = None

from pynput import keyboard

from config import HOTKEY_COMBO, COUNTDOWN_SECONDS, IS_MAC
from gui.unified_window import UnifiedWindow
from engine.typer import Typer

def check_accessibility_permissions():
    if not IS_MAC:
        return True
    
    if AXIsProcessTrusted is None:
        return True
    
    try:
        return AXIsProcessTrusted()
    except:
        return True

def open_accessibility_settings():
    if not IS_MAC:
        return
    
    try:
        subprocess.run([
            "open", "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"
        ], check=False)
    except:
        pass

def open_input_monitoring_settings():
    if not IS_MAC:
        return
    
    try:
        subprocess.run([
            "open", "x-apple.systempreferences:com.apple.preference.security?Privacy_ListenEvent"
        ], check=False)
    except:
        pass

class TextTyperApp:
    def __init__(self):
        self.typer = None
        self.typing_thread = None
        self.total_chars = 0
        self.start_time = 0
        self._countdown_cancelled = False
        
        self.window = UnifiedWindow(
            on_start=self._on_start_typing,
            on_pause=self._on_pause,
            on_resume=self._on_resume,
            on_stop=self._on_stop
        )
        
        self.window.after(300, self._check_permissions)
        self._setup_hotkey()

    def _check_permissions(self):
        if IS_MAC and not check_accessibility_permissions():
            self.window.show_permission_dialog(
                on_open_accessibility=open_accessibility_settings,
                on_open_input_monitoring=open_input_monitoring_settings,
                on_quit=self._quit_app
            )

    def _quit_app(self):
        self.cleanup()
        self.window.destroy()
        sys.exit(0)

    def _setup_hotkey(self):
        try:
            self.hotkey_listener = keyboard.GlobalHotKeys({
                HOTKEY_COMBO: self._trigger_start
            })
            self.hotkey_listener.start()
        except Exception as e:
            print(f"Warning: Could not setup hotkey: {e}")

    def _trigger_start(self):
        self.window.after(0, self.window.trigger_start)

    def _on_start_typing(self, text, settings):
        self._countdown_cancelled = False
        
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
        
        self._run_countdown(text)

    def _run_countdown(self, text):
        def countdown():
            for i in range(COUNTDOWN_SECONDS, 0, -1):
                if self._countdown_cancelled:
                    return
                self.window.after(0, lambda s=i: self.window.show_countdown(s))
                time.sleep(1)
            
            if self._countdown_cancelled:
                return
                
            self.start_time = time.time()
            self.window.after(0, self.window.hide_countdown)
            self.window.after(0, lambda: self.window.update_progress(0, self.total_chars, self.estimated_time))
            
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
        
        self.window.after(0, lambda: self.window.update_progress(current, total, remaining))

    def _on_typing_complete(self):
        self.window.after(0, self.window.on_typing_complete)

    def _on_pause(self):
        if self.typer:
            self.typer.pause()

    def _on_resume(self):
        if self.typer:
            self.typer.resume()

    def _on_stop(self):
        self._countdown_cancelled = True
        if self.typer:
            self.typer.cancel()

    def run(self):
        self.window.mainloop()

    def cleanup(self):
        try:
            self.hotkey_listener.stop()
        except:
            pass
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
