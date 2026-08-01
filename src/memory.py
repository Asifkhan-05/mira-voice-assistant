import json
import os
import sys
sys.path.append(r"D:\VoiceAssistant")
from config import BASE_DIR

MEMORY_FILE = os.path.join(BASE_DIR, "memory.json")

def load_memory():
    """Load memory from file."""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {}

def save_memory(memory):
    """Save memory to file."""
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

def remember(key, value):
    """Store a new memory."""
    memory = load_memory()
    memory[key] = value
    save_memory(memory)
    print(f"💾 Remembered: {key} = {value}")

def recall(key):
    """Retrieve a specific memory."""
    memory = load_memory()
    return memory.get(key, None)

def forget(key):
    """Delete a specific memory."""
    memory = load_memory()
    if key in memory:
        del memory[key]
        save_memory(memory)
        print(f"🗑️ Forgot: {key}")

def get_all_memories():
    """Return all memories as a formatted string for LLM context."""
    memory = load_memory()
    if not memory:
        return ""
    lines = [f"- {k}: {v}" for k, v in memory.items()]
    return "What you know about the user:\n" + "\n".join(lines)

if __name__ == "__main__":
    # Test
    remember("user_name", "Asif")
    remember("user_city", "Bengaluru")
    remember("user_interest", "electronics and AI")
    print(get_all_memories())
    print(recall("user_name"))