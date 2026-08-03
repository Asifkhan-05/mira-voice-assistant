import subprocess
import sounddevice as sd
import soundfile as sf
import sys
sys.path.append(r"D:\VoiceAssistant")
from config import PIPER_EXE, PIPER_OUTPUT, LANGUAGE_MODELS, DEFAULT_LANGUAGE

def speak(text, language="en"):
    print(f"🔊 Speaking ({language}): {text}")
    
    model_path = LANGUAGE_MODELS.get(language, LANGUAGE_MODELS[DEFAULT_LANGUAGE])
    
    subprocess.run(
        [PIPER_EXE, "--model", model_path, "--output_file", PIPER_OUTPUT],
        input=text.encode('utf-8'),
        check=True,
        stderr=subprocess.DEVNULL
    )
    
    data, sr = sf.read(PIPER_OUTPUT)
    sd.play(data, sr)
    sd.wait()

if __name__ == "__main__":
    speak("Hello! I am Athena, your best friend.", language="en")