import webbrowser
import os
import subprocess
import datetime
import sys
sys.path.append(r"D:\VoiceAssistant")
from memory import remember, recall, forget

# Chrome path
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

def get_time():
    now = datetime.datetime.now()
    return f"It's {now.strftime('%I:%M %p')}."

def get_date():
    now = datetime.datetime.now()
    return f"Today is {now.strftime('%A, %B %d %Y')}."

def open_youtube():
    webbrowser.open("https://www.youtube.com")
    return "Opening YouTube for you."

def search_youtube(query):
    url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    webbrowser.open(url)
    return f"Searching YouTube for {query}."

def open_google():
    webbrowser.open("https://www.google.com")
    return "Opening Google for you."

def search_google(query):
    webbrowser.open(f"https://www.google.com/search?q={query.replace(' ', '+')}")
    return f"Searching Google for {query}."

def open_chrome():
    if os.path.exists(CHROME_PATH):
        subprocess.Popen(CHROME_PATH)
        return "Opening Chrome for you."
    return "I couldn't find Chrome on your system."

def open_calculator():
    subprocess.Popen("calc.exe")
    return "Opening calculator."

def open_notepad():
    subprocess.Popen("notepad.exe")
    return "Opening Notepad."

def handle_memory(text):
    text_lower = text.lower()

    if "my name is" in text_lower:
        # Extract only the first word after "my name is"
        after = text_lower.split("my name is")[-1].strip()
        name = after.split()[0].strip(".,!?").capitalize()
        remember("user_name", name)
        return f"Got it! I'll remember that your name is {name}."

    if "i live in" in text_lower:
        after = text_lower.split("i live in")[-1].strip()
        city = after.split()[0].strip(".,!?").capitalize()
        remember("user_city", city)
        return f"Got it! I'll remember that you live in {city}."

    if "i am from" in text_lower:
        after = text_lower.split("i am from")[-1].strip()
        place = after.split()[0].strip(".,!?").capitalize()
        remember("user_city", place)
        return f"Got it! I'll remember you are from {place}."

    if "i like" in text_lower:
        interest = text_lower.split("i like")[-1].strip().strip(".,!?")
        remember("user_interest", interest)
        return f"Got it! I'll remember that you like {interest}."

    if "i love" in text_lower:
        interest = text_lower.split("i love")[-1].strip().strip(".,!?")
        remember("user_interest", interest)
        return f"Nice! I'll remember that you love {interest}."

    if "forget my" in text_lower:
        key = text_lower.split("forget my")[-1].strip().strip(".,!?")
        forget(f"user_{key}")
        return f"Done, I've forgotten your {key}."

    return None

def detect_action(text):
    text_lower = text.lower()

    # Memory first
    memory_result = handle_memory(text)
    if memory_result:
        return memory_result

    # YouTube search — must check before generic YouTube open
    if "youtube" in text_lower and any(w in text_lower for w in ["search", "find", "look up", "play"]):
        # Extract query
        for keyword in ["search for", "search", "find", "look up", "play"]:
            if keyword in text_lower and "youtube" in text_lower:
                # Get everything after the keyword
                parts = text_lower.split(keyword)
                query = parts[-1].replace("in youtube", "").replace("on youtube", "").replace("youtube", "").strip()
                if query:
                    return search_youtube(query)

    # Chrome
    if "chrome" in text_lower:
        return open_chrome()

    # Google search
    if "search" in text_lower and "google" in text_lower:
        if "search for" in text_lower:
            query = text_lower.split("search for")[-1].strip()
        else:
            query = text_lower.split("search")[-1].strip()
        return search_google(query)

    # Generic actions
    if "youtube" in text_lower:
        return open_youtube()
    if "google" in text_lower:
        return open_google()
    if "time" in text_lower:
        return get_time()
    if "date" in text_lower:
        return get_date()
    if "calculator" in text_lower:
        return open_calculator()
    if "notepad" in text_lower:
        return open_notepad()

    return None