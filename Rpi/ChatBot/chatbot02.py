
import getpass
import os
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

# NIVIDIA key, ssbautomation0@gmail.com
# Username: $oauthtoken
# Password: NjNqOHFtbGlzaWI4MjZ1cTR1c3FvcXVwbG86NzBkOTcxNzktMDBkZC00ODZiLTkxYzYtZjU3YzM4YjNkM2Qx

# ~ if not os.environ.get("NVIDIA_API_KEY"):
  # ~ os.environ["NVIDIA_API_KEY"] = "NjNqOHFtbGlzaWI4MjZ1cTR1c3FvcXVwbG86NTE5MTkzODAtNDc3Yy00NzMxLWE2ZGQtOWRmOWE4MzRiMTRj"


if not os.environ.get("OPENAI_API_KEY"):
  os.environ["OPENAI_API_KEY"] = "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"

  
# ~ model = ChatNVIDIA(model="meta/llama3-70b-instruct")
# ~ model = ChatOpenAI(model="gpt-4o-mini")
model = ChatOpenAI(model="gpt-3.5-turbo")

# ~ model.invoke("Hello, world!")


messages = [
    SystemMessage("Translate the following from English into German"),
    HumanMessage("hi!"),
]

# Invoke the model and store the response
response = model.invoke(messages)

# Print the response
print(response)

