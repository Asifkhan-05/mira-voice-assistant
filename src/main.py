import time
from audio import record_audio, save_audio
from stt import transcribe
from tts import speak
from llm import chat
from wake_word import listen_for_wake_word
from actions import detect_action
from memory import recall
import sys
sys.path.append(r"D:\VoiceAssistant")
from config import RECORDING_PATH, ASSISTANT_NAME

def listen_and_respond():
    # Step 1 — Record
    audio, sr = record_audio()
    save_audio(audio, sr, filename=RECORDING_PATH)

    # Step 2 — Transcribe + detect language
    t1 = time.time()
    user_text, detected_language = transcribe(RECORDING_PATH)
    print(f"⏱️ STT took: {time.time() - t1:.2f}s | Language: {detected_language}")

    if not user_text.strip():
        speak("Sorry, I didn't catch that. Could you repeat?")
        return

    print(f"🎤 You said: {user_text}")

    # Step 3 — Actions (English only for now)
    if detected_language == "en":
        action_result = detect_action(user_text)
        if action_result:
            print(f"⚡ Action triggered: {action_result}")
            speak(action_result, language="en")
            return

    # Step 4 — LLM response
    t2 = time.time()
    reply = chat(user_text, language=detected_language)
    print(f"⏱️ LLM took: {time.time() - t2:.2f}s")

    # Step 5 — Speak in detected language
    t3 = time.time()
    speak(reply, language=detected_language)
    print(f"⏱️ TTS took: {time.time() - t3:.2f}s")

def main():
    print("⏳ Loading all models, please wait...")
    from wake_word import model
    from stt import model as stt_model
    print("✅ All models loaded.\n")

    user_name = recall("user_name")
    if user_name:
        speak(f"Welcome back {user_name}! What's up?", language="en")
    else:
        speak(f"Hey! I'm {ASSISTANT_NAME}, your best friend. What's good?", language="en")

    print(f"🎙️ {ASSISTANT_NAME} is ready... (Ctrl+C to stop)\n")

    while True:
        try:
            listen_for_wake_word()
            speak("Yeah?", language="en")
            listen_and_respond()

        except KeyboardInterrupt:
            speak("Catch you later!", language="en")
            print(f"\n👋 {ASSISTANT_NAME} stopped.")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            speak("Something went wrong, give me a sec.", language="en")

if __name__ == "__main__":
    main()