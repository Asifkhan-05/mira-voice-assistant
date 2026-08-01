import time
from audio import record_audio, save_audio
from stt import transcribe
from tts import speak
from llm import chat
from wake_word import listen_for_wake_word
from actions import detect_action
from memory import remember, recall, get_all_memories
import sys
sys.path.append(r"D:\VoiceAssistant")
from config import RECORDING_PATH, ASSISTANT_NAME

def listen_and_respond():
    # Step 1 — Record until silence
    audio, sr = record_audio()
    save_audio(audio, sr, filename=RECORDING_PATH)

    # Step 2 — Transcribe
    t1 = time.time()
    user_text = transcribe(RECORDING_PATH)
    print(f"⏱️ STT took: {time.time() - t1:.2f}s")

    if not user_text.strip():
        speak("Sorry, I didn't catch that. Could you repeat?")
        return

    print(f"🎤 You said: {user_text}")

    # Step 3 — Check actions and memory first
    action_result = detect_action(user_text)
    if action_result:
        print(f"⚡ Action triggered: {action_result}")
        speak(action_result)
        return

    # Step 4 — Fall back to LLM
    t2 = time.time()
    reply = chat(user_text)
    print(f"⏱️ LLM took: {time.time() - t2:.2f}s")

    # Step 5 — Speak reply
    t3 = time.time()
    speak(reply)
    print(f"⏱️ TTS took: {time.time() - t3:.2f}s")

def main():
    print("⏳ Loading all models, please wait...")
    from wake_word import model
    from stt import model as stt_model
    print("✅ All models loaded.\n")

    # Greet user by name if remembered
    user_name = recall("user_name")
    if user_name:
        speak(f"Welcome back {user_name}! How can I help you?")
    else:
        speak(f"Hello! I am {ASSISTANT_NAME}, your voice assistant. How can I help you?")

    print("🎙️ Mira is ready... (Ctrl+C to stop)\n")

    while True:
        try:
            listen_for_wake_word()
            speak("Yes?")
            listen_and_respond()

        except KeyboardInterrupt:
            speak("Goodbye! Talk to you soon.")
            print("\n👋 Mira stopped.")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            speak("Something went wrong, let me try again.")

if __name__ == "__main__":
    main()