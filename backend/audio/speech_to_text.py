from faster_whisper import WhisperModel
import numpy as np
from utils.exceptions import TranscriptionError
import logging

logger = logging.getLogger(__name__)

class SpeechToText:
    def __init__(self):
        try:
            self.model = WhisperModel("small", device="cpu", compute_type="int8")
        except Exception as e:
            raise TranscriptionError(f"Failed to initialize Whisper model: {str(e)}")

    def transcribe(self, audio_data: np.ndarray) -> str:
        if audio_data is None or len(audio_data) == 0:
            raise TranscriptionError("Empty audio data provided")
            
        try:
            segments, info = self.model.transcribe(audio_data, language="en")
            if info.language_probability < -1:     # Low confidence threshold
                logger.warning("Low confidence in transcription")
            return " ".join([segment.text for segment in segments])
        except Exception as e:
            raise TranscriptionError(f"Transcription failed: {str(e)}")