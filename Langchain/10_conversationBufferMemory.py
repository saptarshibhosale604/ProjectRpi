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

## part 01, create a conversation memory
memory = ConversationBufferMemory()

conversation = ConversationChain(
    llm=llm, 
    memory = memory,
    verbose=True
)

conversation.predict(input="Hello, nice to meet you!")

conversation.predict(input="Tell me about the Einstein-Szilard Letter in 2 lines ")

    
print("\n\n## memory.buffer ##:",memory.buffer)

print("\n\n## memory.load_memory_variables({}) ##:",memory.load_memory_variables({}))

memory.save_context({"input": "Very Interesting."}, 
                    {"output": "Yes, it was my pleasure as an AI to answer."})

print("\n\n## memory.load_memory_variables({}) ##:",memory.load_memory_variables({}))


conversation.memory

## part 02, save the conversation memory
pickled_str = pickle.dumps(conversation.memory)

print("\n\n## pickled_str ##:", pickled_str)

with open('memory.pkl','wb') as f:
    f.write(pickled_str)

# ## part 03, load the conversation memory
# new_memory_load = open('memory.pkl','rb').read()

# llm = ChatOpenAI(temperature=0.0)
# reload_conversation = ConversationChain(
#     llm=llm, 
#     memory = pickle.loads(new_memory_load),
#     verbose=True
# )

# print("\n\n## reload_conversation.memory.buffer ##:",reload_conversation.memory.buffer)

