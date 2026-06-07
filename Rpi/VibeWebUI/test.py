import requests

url = "http://localhost:11434/api/chat"

payload = {
    "model": "llama3.2",
    "messages": [
        {
            "role": "user",
            "content": "Hello"
        }
    ],
    "stream": False
}

r = requests.post(url, json=payload)

print(r.status_code)
print(r.text)
