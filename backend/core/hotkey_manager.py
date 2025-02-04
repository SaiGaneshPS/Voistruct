import keyboard
from typing import Callable
import logging
from utils.exceptions import HotkeyError

logger = logging.getLogger(__name__)

class HotkeyManager:
    def __init__(self):
        self.recording_active = False
        self.callback = None
        self.hotkey = None
        
    def register_toggle_hotkey(self, hotkey: str, callback: Callable):
        try:
            self.callback = callback
            self.hotkey = hotkey
            keyboard.on_press_key(hotkey.split('+')[-1], 
                                self._on_press, 
                                suppress=True)
            logger.info(f"Registered hotkey: {hotkey}")
        except Exception as e:
            raise HotkeyError(f"Failed to register hotkey: {str(e)}")

    def _on_press(self, event):
        try:
            hotkey_parts = self.hotkey.split('+')
            if all(keyboard.is_pressed(part) for part in hotkey_parts):
                if not self.recording_active:
                    self.recording_active = True
                    if self.callback:
                        self.callback(True)
        except Exception as e:
            logger.error(f"Error in hotkey press handler: {str(e)}")
            self.recording_active = False

    def stop_recording(self):
        if self.recording_active:
            self.recording_active = False
            if self.callback:
                self.callback(False)

    def start(self):
        """Start listening for hotkeys"""
        keyboard.wait()