import logging
import keyboard
import sys
from core.hotkey_manager import HotkeyManager
from audio.recorder import AudioRecorder
from audio.speech_to_text import SpeechToText
from utils.exceptions import VoistructError
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('voistruct.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class VoistructBackend:
    def __init__(self):
        try:
            self.hotkey_manager = HotkeyManager()
            self.recorder = AudioRecorder()
            self.speech_to_text = SpeechToText()
            self.is_recording = False
        except VoistructError as e:
            logger.error(f"Failed to initialize Voistruct: {str(e)}")
            sys.exit(1)

    def on_hotkey_toggle(self, is_active: bool):
        try:
            if is_active and not self.is_recording:
                logger.info("Starting recording...")
                self.is_recording = True
                self.recorder.start_recording()
            elif not is_active and self.is_recording:
                logger.info("Stopping recording...")
                self.is_recording = False
                audio_data = self.recorder.stop_recording()
                if audio_data is not None:
                    text = self.speech_to_text.transcribe(audio_data)
                    logger.info(f"Transcribed: {text}")
        except VoistructError as e:
            logger.error(f"Error during recording/transcription: {str(e)}")
            self.is_recording = False
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            self.is_recording = False

    def check_key_release(self):
        while True:
            if self.is_recording and not all(keyboard.is_pressed(k) for k in self.hotkey_parts):
                self.hotkey_manager.stop_recording()
            time.sleep(0.1)

    def run(self):
        try:
            hotkey = 'alt'
            self.hotkey_parts = hotkey.split('+')
            self.hotkey_manager.register_toggle_hotkey(hotkey, self.on_hotkey_toggle)
            
            import threading
            release_thread = threading.Thread(target=self.check_key_release, daemon=True)
            release_thread.start()
            
            logger.info("Voistruct backend started. Press ctrl+shift+a to record")
            self.hotkey_manager.start()
        except KeyboardInterrupt:
            logger.info("Shutting down Voistruct...")
        except Exception as e:
            logger.error(f"Fatal error: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    try:
        app = VoistructBackend()
        app.run()
    except Exception as e:
        logger.critical(f"Application failed to start: {str(e)}")
        sys.exit(1)