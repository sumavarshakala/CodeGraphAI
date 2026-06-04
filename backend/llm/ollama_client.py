import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

def generate_answer(prompt: str):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "qwen3:8b",
            "prompt": prompt,
            "stream": False,
        },
        timeout=300,
    )

    response.raise_for_status()

    return response.json()["response"]