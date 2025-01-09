import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

# myTestKey07 #saptarshibhosale604@gmail.com
f = open('openai_api_key.txt')
# print("openai_api_key: ", f.read())

if not os.environ.get("OPENAI_API_KEY"):
  os.environ["OPENAI_API_KEY"] = f.read().strip() 

# # Method 01
# # model = ChatOpenAI(model="gpt-4o-mini")
# model = ChatOpenAI(model="gpt-3.5-turbo")

# messages = [
#     SystemMessage("Translate the following from English into German"),
#     HumanMessage("hi!"),
# ]

# # Invoke the model and store the response
# response = model.invoke(messages)

# # Print the response
# print(response)

# Method 02
llm = ChatOpenAI()
response = llm.invoke("Here is a fun fact about Pluto:")

# Print the response
print(response)
