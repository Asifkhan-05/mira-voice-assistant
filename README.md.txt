# Mira — Local Voice Assistant

A fully local, independent voice assistant built with Python.
No OpenAI, no Google API, no internet required. Runs entirely on your machine.

## Pipeline
- Wake Word — openWakeWord (Hey Jarvis)
- Speech to Text — faster-whisper (tiny model)
- Brain — Ollama + llama3.2:1b (local LLM)
- Text to Speech — Piper TTS

## Features
- Wake word detection
- Natural conversation via local LLM
- Remembers your name, city, interests across sessions
- Open apps (Chrome, YouTube, Calculator, Notepad)
- Search Google and YouTube by voice
- Tell time and date
- Fully offline — no API keys needed

## Requirements
- Python 3.9+
- Ollama installed with llama3.2:1b model
- Piper TTS executable + voice model
- Windows (tested on Windows 11)

## Setup

1. Clone the repo
git clone https://github.com/Asifkhan-05/mira-voice-assistant
cd mira-voice-assistant

2. Create virtual environment
python -m venv venv
venv\Scripts\activate

3. Install dependencies
pip install -r requirements.txt

4. Install Ollama
Download from https://ollama.com/download
Then run: ollama pull llama3.2:1b

5. Download Piper
Download piper_windows_amd64.zip from
https://github.com/rhasspy/piper/releases/latest
Extract to models/piper/piper/
Download en_US-lessac-low.onnx and en_US-lessac-low.onnx.json
to the same folder

6. Run
python src/main.py

## Project Structure
VoiceAssistant/
├── src/
│   ├── main.py        # Main loop
│   ├── audio.py       # Mic input + VAD
│   ├── stt.py         # Speech to text
│   ├── tts.py         # Text to speech
│   ├── llm.py         # LLM brain
│   ├── wake_word.py   # Wake word detection
│   ├── actions.py     # Actions (open apps, search)
│   └── memory.py      # Persistent memory
├── config.py          # All settings in one place
├── requirements.txt
└── README.md

## Built by
Asif Khan — EEE Student, REVA University Bengaluru
GitHub: github.com/Asifkhan-05