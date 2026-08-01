import sounddevice as sd
import soundfile as sf
import numpy as np
import sys
sys.path.append(r"D:\VoiceAssistant")
from config import SAMPLE_RATE

CHUNK_DURATION = 0.03           # 30ms chunks
CHUNK_SIZE = int(SAMPLE_RATE * CHUNK_DURATION)
SILENCE_LIMIT = 1.5             # seconds of silence before stopping
MIN_SPEECH = 0.5                # minimum seconds of speech
SILENCE_THRESHOLD = 0.01        # volume below this = silence

def is_silent(chunk):
    """Check if audio chunk is silent based on volume."""
    rms = np.sqrt(np.mean(chunk ** 2))
    return rms < SILENCE_THRESHOLD

def record_audio(sample_rate=SAMPLE_RATE):
    print("🎤 Listening... (speak now, stops when you pause)")

    audio_chunks = []
    silent_chunks = 0
    speech_chunks = 0

    max_silent_chunks = int(SILENCE_LIMIT / CHUNK_DURATION)
    min_speech_chunks = int(MIN_SPEECH / CHUNK_DURATION)

    with sd.InputStream(samplerate=sample_rate, channels=1,
                       dtype='float32', blocksize=CHUNK_SIZE) as stream:
        while True:
            chunk, _ = stream.read(CHUNK_SIZE)
            chunk_flat = chunk.flatten()
            audio_chunks.append(chunk_flat)

            if is_silent(chunk_flat):
                silent_chunks += 1
                # Stop only after enough speech then silence
                if speech_chunks > min_speech_chunks and silent_chunks > max_silent_chunks:
                    print("✅ Done listening.")
                    break
            else:
                speech_chunks += 1
                silent_chunks = 0  # reset silence counter

    audio = np.concatenate(audio_chunks)
    return audio, sample_rate

def save_audio(audio, sample_rate, filename="temp_recording.wav"):
    sf.write(filename, audio, sample_rate)

def play_audio(filename="temp_recording.wav"):
    data, sr = sf.read(filename)
    sd.play(data, sr)
    sd.wait()