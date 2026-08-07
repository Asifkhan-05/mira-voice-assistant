import time
import threading
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
from hud import start_hud, get_hud, AthenaState

def listen_and_respond():
    hud = get_hud()

    # Step 1 — Record
    if hud:
        hud.update_state_signal.emit(AthenaState.LISTENING)
    audio, sr = record_audio()
    save_audio(audio, sr, filename=RECORDING_PATH)

    # Step 2 — Transcribe
    if hud:
        hud.update_state_signal.emit(AthenaState.THINKING)
    t1 = time.time()
    user_text, detected_language = transcribe(RECORDING_PATH)
    print(f"⏱️ STT took: {time.time() - t1:.2f}s")

    if not user_text.strip():
        speak("Sorry, I didn't catch that. Could you repeat?")
        return

    print(f"🎤 You said: {user_text}")
    if hud:
        hud.update_user_signal.emit(user_text)

    # Step 3 — Actions
    action_result = detect_action(user_text)
    if action_result:
        print(f"⚡ Action triggered: {action_result}")
        if hud:
            hud.update_state_signal.emit(AthenaState.SPEAKING)
            hud.update_response_signal.emit(action_result)
        speak(action_result, language="en")
        if hud:
            hud.update_state_signal.emit(AthenaState.SLEEPING)
        return

    # Step 4 — LLM
    t2 = time.time()
    reply = chat(user_text, language=detected_language)
    print(f"⏱️ LLM took: {time.time() - t2:.2f}s")

    # Step 5 — Speak
    if hud:
        hud.update_state_signal.emit(AthenaState.SPEAKING)
        hud.update_response_signal.emit(reply)
    t3 = time.time()
    speak(reply, language=detected_language)
    print(f"⏱️ TTS took: {time.time() - t3:.2f}s")
    if hud:
        hud.update_state_signal.emit(AthenaState.SLEEPING)

def voice_loop():
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
            hud = get_hud()
            if hud:
                hud.update_state_signal.emit(AthenaState.SLEEPING)
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

def main():
    # Start HUD in main thread
    app, hud = start_hud()

    # Run voice loop in background thread
    voice_thread = threading.Thread(target=voice_loop, daemon=True)
    voice_thread.start()

    # Run Qt event loop
    app.exec_()

if __name__ == "__main__":
    main()