from faster_whisper import WhisperModel

# Using 'base' model — good balance of speed and accuracy for 8GB RAM
MODEL_SIZE = "tiny"

print("⏳ Loading Whisper model...")
model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
print("✅ Whisper model loaded.")

def transcribe(audio_path="test_recording.wav"):
    print("🧠 Transcribing...")
    segments, info = model.transcribe(audio_path, beam_size=5, language="en")
    
    full_text = ""
    for segment in segments:
        full_text += segment.text + " "
    
    full_text = full_text.strip()
    print(f"📝 You said: {full_text}")
    return full_text

if __name__ == "__main__":
    # Test: transcribe the recording from audio.py
    import sounddevice as sd
    import soundfile as sf
    import numpy as np
    from audio import record_audio, save_audio

    audio, sr = record_audio(duration=5)
    save_audio(audio, sr)
    result = transcribe("test_recording.wav")
    print(f"\n Result: '{result}'")