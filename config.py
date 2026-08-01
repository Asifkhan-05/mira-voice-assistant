import os

# ─── Paths ───────────────────────────────────────────────
BASE_DIR = r"D:\VoiceAssistant"
MODELS_DIR = os.path.join(BASE_DIR, "models")

# Piper TTS
PIPER_EXE = os.path.join(MODELS_DIR, "piper", "piper", "piper.exe")
PIPER_MODEL = os.path.join(MODELS_DIR, "piper", "piper", "en_US-lessac-low.onnx")
PIPER_OUTPUT = os.path.join(MODELS_DIR, "piper", "piper", "response.wav")

# Temp recording
RECORDING_PATH = os.path.join(BASE_DIR, "temp_recording.wav")

# ─── STT Settings ────────────────────────────────────────
WHISPER_MODEL_SIZE = "tiny"     # tiny / base / small
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
ASSISTANT_NAME = "Mira"
SYSTEM_PROMPT = f"""
You are {ASSISTANT_NAME}, a witty and helpful voice assistant.
You DO have memory and CAN remember things the user tells you.
STRICT RULE: Reply in 1 sentence only, maximum 15 words.
Never use bullet points, markdown, or special characters.
Natural spoken sentences only.
"""