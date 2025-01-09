
import getpass
import os
# from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

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

