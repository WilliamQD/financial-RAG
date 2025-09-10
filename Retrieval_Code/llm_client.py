from openai import OpenAI
from config import OPENAI_API_KEY

import ollama

client = OpenAI(api_key=OPENAI_API_KEY)

def ollama_chat(messages, model="deepseek-r1", stream=False):
    """
    Use the Ollama API to chat with a model. Does not work on HPC.
    """
    return ollama.chat(
        model=model,
        messages=messages,
        stream=stream
    )
    
