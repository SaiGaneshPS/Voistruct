class VoistructError(Exception):
    """Base exception for Voistruct"""
    pass

class AudioError(VoistructError):
    """Audio related errors"""
    pass

class DeviceError(AudioError):
    """Audio device errors"""
    pass

class TranscriptionError(VoistructError):
    """Speech to text errors"""
    pass

class HotkeyError(VoistructError):
    """Hotkey registration/handling errors"""
    pass

class ClassificationError(VoistructError):
    """Classification errors"""
    pass

