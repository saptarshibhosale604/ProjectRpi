# # app.py
# import ollama


# def main():
#     # Example usage of the Ollama library
#     model = ollama.load("llama3.2:1b")
#     result = model.predict("Who is the Prime Minister of India")
#     print(result)

# if __name__ == "__main__":
#     main()


from ollama import chat
from ollama import ChatResponse

print("initialized")

# simple one question answer
def Main02():
    response: ChatResponse = chat(model='llama3.2:1b', messages=[
    {
        'role': 'user',
        'content': 'Why is the sky blue?',
    },
    ])
    print(response['message']['content'])
    # or access fields directly from the response object
    print(response.message.content)

# conversation, no context awareness
# def Main03():
#     while True:
#         userInput = input("Enter your input: ")
#         response: ChatResponse = chat(model='llama3.2:1b', messages=[
#         {
#             'role': 'user',
#             'content': userInput,
#         },
#         ])
#         print(response['message']['content'])
#         # or access fields directly from the response object
#         # print(response.message.content)

# from ollama import chat

# def Main():

#     stream = chat(
#         model='llama3.2',
#         messages=[{'role': 'user', 'content': 'Why is the sky blue?'}],
#         stream=True,
#     )

#     for chunk in stream:
#     print(chunk['message']['content'], end='', flush=True)

from ollama import chat

# Initialize message history
messages = []

print("Welcome to ChatBot! Type 'exit' to quit.\n")

def Main():
    while True:
        user_input = input("You: ")

        if user_input.lower() in ['exit', 'quit']:
            print("Goodbye!")
            break

        # Add user message to history
        messages.append({'role': 'user', 'content': user_input})

        # Get response from the model
        stream = chat(
            model='llama3.2:1b',
            messages=messages,
            stream=True,
        )

        # Collect response and print it
        response = ""
        print("Bot: ", end='', flush=True)
        for chunk in stream:
            content = chunk['message']['content']
            print(content, end='', flush=True)
            response += content
            
        print()

        # Add assistant response to history
        messages.append({'role': 'assistant', 'content': response})

Main()
print("ended")


# import os
# import requests

# print("initialized")

# OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11435")

# def generate_response(prompt):
#     response = requests.post(f"{OLLAMA_BASE_URL}/api/generate", json={
#         "model": "llama3",  # or any model pulled into Ollama
#         "prompt": prompt
#     })
#     return response.json()["response"]

# print(generate_response("Hello, who are you?"))

# print("ended")