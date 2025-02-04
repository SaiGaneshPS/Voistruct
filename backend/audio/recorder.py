import pyaudio
import wave
import threading
from typing import Optional
from utils.exceptions import AudioError, DeviceError
import logging
import numpy as np

logger = logging.getLogger(__name__)

class AudioRecorder:
    def __init__(self):
        try:
            self.audio = pyaudio.PyAudio()
            self._check_audio_devices()
        except Exception as e:
            raise DeviceError(f"Failed to initialize audio system: {str(e)}")

        self.stream: Optional[pyaudio.Stream] = None
        self.recording = False
        self.frames = []
    
    def _check_audio_devices(self):
        """Verify audio input devices"""
        input_devices = []
        for i in range(self.audio.get_device_count()):
            device_info = self.audio.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                input_devices.append(device_info)
        
        if not input_devices:
            raise DeviceError("No input devices found")
        
    import pyaudio
import wave
import threading
from typing import Optional
import numpy as np
from utils.exceptions import AudioError, DeviceError
import logging

logger = logging.getLogger(__name__)

class AudioRecorder:
    def __init__(self):
        try:
            self.audio = pyaudio.PyAudio()
            self._check_audio_devices()
        except Exception as e:
            raise DeviceError(f"Failed to initialize audio system: {str(e)}")
        
        self.stream: Optional[pyaudio.Stream] = None
        self.recording = False
        self.frames = []

    def _check_audio_devices(self):
        """Verify audio input devices"""
        input_devices = []
        for i in range(self.audio.get_device_count()):
            device_info = self.audio.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                input_devices.append(device_info)
        
        if not input_devices:
            raise DeviceError("No input devices found")
        
    def start_recording(self):
        if not self.recording:
            try:
                self.recording = True
                self.frames = []
                self.stream = self.audio.open(
                    format=pyaudio.paFloat32,
                    channels=1,
                    rate=16000,
                    input=True,
                    frames_per_buffer=1024,
                    stream_callback=self._audio_callback
                )
                self.stream.start_stream()
            except Exception as e:
                self.recording = False
                raise AudioError(f"Failed to start recording: {str(e)}")

    def _audio_callback(self, in_data, frame_count, time_info, status):
        try:
            if status:
                logger.warning(f"Audio callback status: {status}")
            if self.recording:
                self.frames.append(np.frombuffer(in_data, dtype=np.float32))
            return (in_data, pyaudio.paContinue)
        except Exception as e:
            logger.error(f"Audio callback error: {str(e)}")
            return (in_data, pyaudio.paAbort)

    def stop_recording(self):
        if self.stream and self.recording:
            try:
                self.recording = False
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None
                return np.concatenate(self.frames) if self.frames else None
            except Exception as e:
                raise AudioError(f"Failed to stop recording: {str(e)}")
        return None

    def __del__(self):
        try:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
            self.audio.terminate()
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")