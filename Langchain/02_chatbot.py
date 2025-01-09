
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

# result = chat.invoke([SystemMessage(content='You are a very rude teenager who only wants to party and not answer questions'),
#                HumanMessage(content='Can you tell me a fact about Earth?')])

# NEEDS TO BE A LIST!
# result = chat.generate([
#   [SystemMessage(content='You are a very rude teenager who only wants to party and not answer questions'),
#   HumanMessage(content='Can you tell me a fact about Earth?')],
#   [SystemMessage(content='You are a University Professor'),
#   HumanMessage(content='Can you tell me a fact about Earth?')]
#   ])

# result = chat.invoke([HumanMessage(content='Can you tell me a fact about Earth?')],
#                  temperature=2,presence_penalty=2,max_tokens=10)
# Print the response
# print(result)
# print(result.content)

# Method 02
llm = ChatOpenAI()
# response = llm.invoke("Here is a fun fact about Pluto:")
from langchain_core.globals import set_llm_cache
from langchain_core.caches import InMemoryCache

set_llm_cache(InMemoryCache())

# The first time, it is not yet in cache, so it should take longer
print("Here01")
response01 = llm.invoke("Tell me a fact about Mars")
print("response01:", response01)

delay(5000)
print("Here02")
response02 = llm.invoke("Tell me a fact about Mars")
print("response02:", response01)

# # Print the response
# print(response)

