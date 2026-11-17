import requests

url = "http://localhost:11434/api/chat"

data = {
    "model": "gemma2:2b",
    "messages": [
        {
            "role": "user",
            "content": "Explain the Digital Personal Data Protection Act in one simple sentence."
        }
    ],
    "stream": False
}

response = requests.post(url, json=data)

print(response.json()["message"]["content"])