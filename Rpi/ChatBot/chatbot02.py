# import getpass
import os
# from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

# myTestKey05

if not os.environ.get("OPENAI_API_KEY"):
  os.environ["OPENAI_API_KEY"] = "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"

# ~ model = ChatOpenAI(model="gpt-4o-mini")
model = ChatOpenAI(model="gpt-3.5-turbo")

messages = [
    SystemMessage("Translate the following from English into German"),
    HumanMessage("hi!"),
]

# Invoke the model and store the response
response = model.invoke(messages)
# llm = ChatOpenAI()
# response = ChatOpenAI().invoke("Here is a fun fact about Pluto:")

# Print the response
print(response)

# llm = ChatOpenAI(openai_api_key=os.environ["OPENAI_API_KEY"])

# print(llm('Here is a fun fact about Pluto:'))

