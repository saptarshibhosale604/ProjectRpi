# app.py
import ollama

print("initialized")

def main():
    # Example usage of the Ollama library
    model = ollama.load("llama3.2:1b")
    result = model.predict("Who is the Prime Minister of India")
    print(result)

if __name__ == "__main__":
    main()

print("ended")
