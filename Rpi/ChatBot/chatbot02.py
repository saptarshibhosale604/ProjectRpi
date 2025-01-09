
import getpass
import os
# from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

#myTestKey03 

if not os.environ.get("OPENAI_API_KEY"):
  os.environ["OPENAI_API_KEY"] = "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"

# # ~ model = ChatOpenAI(model="gpt-4o-mini")
# model = ChatOpenAI(model="gpt-3.5-turbo")

# messages = [
#     SystemMessage("Translate the following from English into German"),
#     HumanMessage("hi!"),
# ]

# Invoke the model and store the response
# response = model.invoke(messages)
# llm = ChatOpenAI()
response = ChatOpenAI().invoke("Here is a fun fact about Pluto:")

# Print the response
print(response)

# llm = ChatOpenAI(openai_api_key=os.environ["OPENAI_API_KEY"])

# print(llm('Here is a fun fact about Pluto:'))

