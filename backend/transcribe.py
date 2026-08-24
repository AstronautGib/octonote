"""
Local speech-to-text using faster-whisper (runs entirely on your machine, no API key needed).

Model sizes (smallest -> largest, speed vs accuracy tradeoff):
  tiny, base, small, medium, large-v3

"base" is a good default for a first pass. Bump to "small" or "medium" if
accuracy on medical terminology matters more than speed.
"""

from faster_whisper import WhisperModel

_MODEL_CACHE = {}


def get_model(model_size: str = "base", device: str = "cpu", compute_type: str = "int8") -> WhisperModel:
    """
    Load (and cache) a faster-whisper model. First call downloads the model
    weights to disk; later calls reuse the cached instance.
    """
    key = (model_size, device, compute_type)
    if key not in _MODEL_CACHE:
        _MODEL_CACHE[key] = WhisperModel(model_size, device=device, compute_type=compute_type)
    return _MODEL_CACHE[key]


def transcribe_audio(audio_path: str, model_size: str = "base") -> str:
    """
    Transcribe an audio file to plain text.

    Args:
        audio_path: path to an audio file (wav, mp3, m4a, etc.)
        model_size: which Whisper model to use

    Returns:
        The full transcript as a single string.
    """
    model = get_model(model_size)
    segments, _info = model.transcribe(audio_path, beam_size=5)
    return " ".join(segment.text.strip() for segment in segments).strip()
