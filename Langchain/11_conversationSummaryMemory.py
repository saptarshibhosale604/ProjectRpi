from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
import pickle

import os

# myTestKey07 #saptarshibhosale604@gmail.com
f = open('openai_api_key.txt')
# print("openai_api_key: ", f.read())

if not os.environ.get("OPENAI_API_KEY"):
  os.environ["OPENAI_API_KEY"] = f.read().strip() 

llm = ChatOpenAI(temperature=0.0)
memory = ConversationSummaryBufferMemory(llm=llm, max_token_limit=100)

conversation = ConverstionChain(llm=llm, memory=memory)

conversation.predict("Give me 4 sentence travel plan for mumbai")

conversation.predict("Give me 4 sentence travel plan for delhi")

print("\n\n## memory.load_memory_variables({}) ##:", memory.load_memory_variables({}))
