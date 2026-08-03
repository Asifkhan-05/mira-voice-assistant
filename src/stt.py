from faster_whisper import WhisperModel
import sys
sys.path.append(r"D:\VoiceAssistant")
from config import WHISPER_MODEL_SIZE, WHISPER_BEAM_SIZE

print("⏳ Loading Whisper model...")
model = WhisperModel(WHISPER_MODEL_SIZE, device="cpu", compute_type="int8")
print("✅ Whisper model loaded.")

def transcribe(audio_path):
    print("🧠 Transcribing...")
    segments, info = model.transcribe(
        audio_path,
        beam_size=WHISPER_BEAM_SIZE,
        language="en"
    )
    full_text = " ".join([s.text for s in segments]).strip()
    print(f"📝 You said: {full_text}")
    return full_text, "en"