import os

# ─── Paths ───────────────────────────────────────────────
BASE_DIR = r"D:\VoiceAssistant"
MODELS_DIR = os.path.join(BASE_DIR, "models")

# Piper TTS
PIPER_EXE = os.path.join(MODELS_DIR, "piper", "piper", "piper.exe")
PIPER_MODEL = os.path.join(MODELS_DIR, "piper", "piper", "en_US-libritts-high.onnx")
PIPER_OUTPUT = os.path.join(MODELS_DIR, "piper", "piper", "response.wav")

# Temp recording
RECORDING_PATH = os.path.join(BASE_DIR, "temp_recording.wav")

# ─── STT Settings ────────────────────────────────────────
WHISPER_MODEL_SIZE = "small"     # tiny / base / small
WHISPER_LANGUAGE = "en"
WHISPER_BEAM_SIZE = 5

# ─── LLM Settings ────────────────────────────────────────
OLLAMA_MODEL = "llama3.2:1b"   # change to phi3:mini if you upgrade RAM

# ─── Wake Word Settings ──────────────────────────────────
WAKE_WORD_MODEL = "hey_jarvis"
WAKE_WORD_THRESHOLD = 0.1

# ─── Recording Settings ──────────────────────────────────
SAMPLE_RATE = 16000
RECORD_DURATION = 3             # seconds to record after wake word

# ─── Personality ─────────────────────────────────────────
ASSISTANT_NAME = "Athena"

SYSTEM_PROMPT = f"""
You are {ASSISTANT_NAME}, the user's best friend who happens to be super smart and helpful.
Talk casually like a real friend — use "yeah", "totally", "no way", "gotcha" naturally.
STRICT RULE: Maximum 1 sentence, 15 words only. Never more.
IMPORTANT: You cannot open files or apps yourself — those are handled separately.
Never pretend to do something you can't. Be honest but friendly.
Never sound robotic or formal. Be warm and witty.
Never use bullet points, markdown, or special characters.
"""

# ─── Language Settings ───────────────────────────────────
# ─── Language Settings ───────────────────────────────────
LANGUAGE_MODELS = {
    "en": os.path.join(MODELS_DIR, "piper", "piper", "en_US-lessac-low.onnx"),
}

DEFAULT_LANGUAGE = "en"