import subprocess
import sounddevice as sd
import soundfile as sf
import sys
sys.path.append(r"D:\VoiceAssistant")
from config import PIPER_EXE, PIPER_MODEL, PIPER_OUTPUT

def speak(text):
    print(f"🔊 Speaking: {text}")
    subprocess.run(
        [PIPER_EXE, "--model", PIPER_MODEL, "--output_file", PIPER_OUTPUT],
        input=text.encode(),
        check=True,
        stderr=subprocess.DEVNULL
    )
    data, sr = sf.read(PIPER_OUTPUT)
    sd.play(data, sr)
    sd.wait()