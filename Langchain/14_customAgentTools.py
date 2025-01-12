from langchain.agents import load_tools, initialize_agent, AgentType

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI


import os

# myTestKey07 #saptarshibhosale604@gmail.com
f = open('openai_api_key.txt')
# print("openai_api_key: ", f.read())

if not os.environ.get("OPENAI_API_KEY"):
  os.environ["OPENAI_API_KEY"] = f.read().strip() 

@tool
def coolest_guy(text :str) -> str:
	'''Returns the name of the coolest person in the universe.
	Expects an input of an empty string '' and returns the 
	name of the coolest person in the universe
	'''
	return "Saptarshi Bhosale"

# ~ model = ChatOpenAI(model="gpt-4o")
llm = ChatOpenAI(temperature=0)
tools = load_tools(['wikipedia', 'llm-math'], llm=llm)
tools += [coolest_guy]
	
agent = initialize_agent(tools, llm, agent = AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)

result = agent.invoke("Who's the coolest person in the universe")

print(result)
