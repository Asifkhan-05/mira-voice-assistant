import openwakeword
import sounddevice as sd
import numpy as np
from openwakeword.model import Model
import sys
sys.path.append(r"D:\VoiceAssistant")
from config import WAKE_WORD_MODEL, WAKE_WORD_THRESHOLD, SAMPLE_RATE, ASSISTANT_NAME

openwakeword.utils.download_models()
model = Model(wakeword_models=[WAKE_WORD_MODEL], inference_framework="onnx")

CHUNK_SIZE = 1280

def listen_for_wake_word():
    print(f"😴 {ASSISTANT_NAME} is sleeping... say 'Hey Jarvis' to wake her up")
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1,
                       dtype='int16', blocksize=CHUNK_SIZE) as stream:
        while True:
            chunk, _ = stream.read(CHUNK_SIZE)
            audio_flat = np.squeeze(chunk)
            prediction = model.predict(audio_flat)
            score = list(prediction.values())[0]
            if score > WAKE_WORD_THRESHOLD:
                print(f"🟢 Wake word detected! {ASSISTANT_NAME} is listening...")
                return True