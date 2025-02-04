import pyaudio
import wave
import threading
from typing import Optional
import numpy as np

class AudioRecorder:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.stream: Optional[pyaudio.Stream] = None
        self.recording = False
        self.frames = []
        
    def start_recording(self):
        if not self.recording:
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

    def _audio_callback(self, in_data, frame_count, time_info, status):
        if self.recording:
            self.frames.append(np.frombuffer(in_data, dtype=np.float32))
        return (in_data, pyaudio.paContinue)

    def stop_recording(self):
        if self.stream and self.recording:
            self.recording = False
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
            return np.concatenate(self.frames) if self.frames else None
        return None

    def __del__(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.audio.terminate()