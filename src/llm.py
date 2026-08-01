import ollama
import sys
sys.path.append(r"D:\VoiceAssistant")
from config import OLLAMA_MODEL, SYSTEM_PROMPT, ASSISTANT_NAME
from memory import get_all_memories

conversation_history = []

def chat(user_input):
    # Build system prompt with memories explicitly injected
    memories = get_all_memories()
    
    if memories:
        full_system_prompt = SYSTEM_PROMPT + f"""

IMPORTANT — facts you already know about the user, use these in your responses:
{memories}
Never say you don't know the user's name or details if they are listed above.
"""
    else:
        full_system_prompt = SYSTEM_PROMPT

    conversation_history.append({
        "role": "user",
        "content": user_input
    })

    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[
            {"role": "system", "content": full_system_prompt}
        ] + conversation_history
    )

    reply = response["message"]["content"]

    conversation_history.append({
        "role": "assistant",
        "content": reply
    })

    print(f"🤖 Mira: {reply}")
    return reply