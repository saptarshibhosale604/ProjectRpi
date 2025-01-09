import time
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain.prompts import (
    ChatPromptTemplate,
    PromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
# myTestKey07 #saptarshibhosale604@gmail.com
f = open('openai_api_key.txt')
# print("openai_api_key: ", f.read())

if not os.environ.get("OPENAI_API_KEY"):
  os.environ["OPENAI_API_KEY"] = f.read().strip() 

# Method 01
# model = ChatOpenAI(model="gpt-4o-mini")
# model = ChatOpenAI(model="gpt-3.5-turbo")
chat = ChatOpenAI()

system_template="You are an AI recipe assistant that specializes in {dietary_preference} dishes that can be prepared in {cooking_time}."
system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)

human_template="{recipe_request}"
human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

print("inputVars:", chat_prompt.input_variables)

# get a chat completion from the formatted messages
request = chat_prompt.format_prompt(cooking_time="5 min", dietary_preference="veg", recipe_request="maggie").to_messages()

print("request:", request)

result = chat.invoke(request)

print("result:::::", result)
# Method 02
# llm = ChatOpenAI()
# # response = llm.invoke("Here is a fun fact about Pluto:")
# from langchain_core.globals import set_llm_cache
# from langchain_core.caches import InMemoryCache

# set_llm_cache(InMemoryCache())

# # The first time, it is not yet in cache, so it should take longer
# print("Here01")
# response01 = llm.invoke("Tell me a fact about Mars")
# print("response01:", response01)

# Delay for 5 seconds
# time.sleep(5)

# print("Here02")
# response02 = llm.invoke("Tell me a fact about Mars")
# print("response02:", response01)

# # Print the response
# print(response)
