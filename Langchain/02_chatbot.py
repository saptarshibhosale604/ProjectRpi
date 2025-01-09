
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
# from langchain.schema import (
#     AIMessage,
#     HumanMessage,
#     SystemMessage
# )

# myTestKey07 #saptarshibhosale604@gmail.com
f = open('openai_api_key.txt')
# print("openai_api_key: ", f.read())

if not os.environ.get("OPENAI_API_KEY"):
  os.environ["OPENAI_API_KEY"] = f.read().strip() 

# Method 01
# model = ChatOpenAI(model="gpt-4o-mini")
# model = ChatOpenAI(model="gpt-3.5-turbo")
chat = ChatOpenAI()

# result = chat.invoke([HumanMessage(content="Can you tell me a fact about Earth?")])

result = chat.invoke([SystemMessage(content='You are a very rude teenager who only wants to party and not answer questions'),
               HumanMessage(content='Can you tell me a fact about Earth?')])
# messages = [
#     SystemMessage("Translate the following from English into German"),
#     HumanMessage("hi!"),
# ]

# Invoke the model and store the response
# response = model.invoke(messages)

# Print the response
print(result.content)

# Method 02
# llm = ChatOpenAI()
# response = llm.invoke("Here is a fun fact about Pluto:")

# # Print the response
# print(response)

