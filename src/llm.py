import ollama
import sys
sys.path.append(r"D:\VoiceAssistant")
from config import OLLAMA_MODEL, ASSISTANT_NAME
from memory import get_all_memories

conversation_history = []

def chat(user_input, language="en"):
    memories = get_all_memories()

    language_instructions = {
        "en": "Always respond in English.",
        "te": "Always respond in Telugu script.",
    }

    lang_instruction = language_instructions.get(language, "Always respond in English.")

    system_prompt = f"""
You are {ASSISTANT_NAME}, the user's best friend who happens to be super smart and helpful.
Talk casually like a real friend — use natural expressions for whatever language you're speaking.
Keep responses to 1-2 sentences max, 30 words max.
Never sound robotic or formal. Be warm, fun, occasionally witty.
Never use bullet points, markdown, or special characters.
{lang_instruction}
"""
    if memories:
        system_prompt += f"\n\nWhat you know about the user:\n{memories}"

    conversation_history.append({
        "role": "user",
        "content": user_input
    })

    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[
            {"role": "system", "content": system_prompt}
        ] + conversation_history
    )

    reply = response["message"]["content"]

    conversation_history.append({
        "role": "assistant",
        "content": reply
    })

    print(f"🤖 Athena: {reply}")
    return reply