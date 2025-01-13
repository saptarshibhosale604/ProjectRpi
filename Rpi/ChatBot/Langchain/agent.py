## ## IMPORTING ## ## 

from langchain_openai import ChatOpenAI

from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from langchain_community.tools import toolShell
from langchain_community.tools import YouTubeSearchTool

import os


## ## API KEYS ## ## 

def RemoveSpaces(input_string):
    # Remove spaces from the input string
    return input_string.replace(" ", "")

openai_key = "sk-proj-zP6XLa1m5gtlBcXJCaHZGmAvXEvUrP 5ATJSPBfLRdEuF-vSroLAG4V0zBdpwPz9PTXe9rM0-CgT3BlbkFJ83 AZyS7Zds5OT4G7S7MJslTok1O8P7ftX6Zz_IvdtMsy_CnjJeBoOv-o-G5t13-1Yw20ei_BwA" # myTestKey08, saptarshibhosale604@gmail.com
tavily_key = "tvly-kX76LCz C36oih0u9COcf6oa 53A47MX0g"

os.environ["OPENAI_API_KEY"] = RemoveSpaces(openai_key)
os.environ["TAVILY_API_KEY"] = RemoveSpaces(tavily_key)

## ## INITIALIZATION ## ## 

## Initializing llm models
llm = ChatOpenAI(model="gpt-3.5-turbo", max_tokens=500, temperature=0, max_retries=1)

## Initializing tools

toolShell = toolShell(ask_human_input=False, verbose=True)
toolShell.description = toolShell.description + f"args {toolShell.args}".replace("{", "{{").replace("}", "}}")

toolYoutube = YouTubeSearchTool()

toolsAdvance =  [toolShell]               	# Need for human in loop
toolsBasic = [toolYoutube]                  # No need for human in loop

tools = toolsAdvance + toolsBasic
print("## ## tools:", tools)

## memory
config = {"configurable": {"thread_id": "thread-1"}}

## UserInput
# ~ userInput = "Tell me where is 13_agentBasic.py file in my pc"
# ~ userInput = "step 1: Tell me where is 13_agentBasic.py file and step 2: then find other python files from same folder"
# ~ userInput = "start a timer for 10 sec and after timer over play alarm clock sound to notify"
# ~ userInput = "play blue eyes by honey singh youtube video on the firefox app"
# ~ userInput = "play blue eyes by honey singh youtube video using firefox cmd in background"
# ~ userInput = "play doku punjabi song youtube video using firefox cmd in background"
# ~ userInput = "start the stopwatch in terminal"
# ~ userInput = "start the timer for 5 sec and notify with alarm clock sound"
# userInput = "tell me storage information"
# ~ userInput = "get link for blue eyes by honey singh youtube video and then run the 1st link using only firefox cmd"
# ~ userInput = "play blue eyes by honey singh youtube video"
# ~ userInput = "find the location of lanchain dir and then Give me the list of python files from that langchain directory"
# ~ userInput = "find the location of 'Lanchain' dir"
# userInput = "Give me 1 link of youtube video of linux"

## other
loopCounter = 0

## graph and agent
graph = create_react_agent(
	llm, 
	tools, 
	interrupt_before=["toolsAdvance"], 
	checkpointer=MemorySaver()
)


## ## SCRIPTS ## ##
def print_stream(graph, inputs, config):
	for s in graph.stream(inputs, config, stream_mode="values"):
		message = s["messages"][-1]
		if isinstance(message, tuple):
			print(message)
		else:
			message.pretty_print()



# Main loop to process the graph
def AgentCall(userInput):
	inputs = {"messages": [("user", userInput)]}  # Replace with actual input
	
	while True:
		if(loopCounter == 0):
			print_stream(graph, inputs, config)
		else:
			print_stream(graph, None, config)
			
		loopCounter += 1
		snapshot = graph.get_state(config)
		
		# Check if the graph has ended
		if not snapshot.next:  # If `snapshot.next` is None or empty, the graph is finished
			print("### Graph has ended.")
			break

		# Get the list of called tools
		existing_message = snapshot.values["messages"][-1]
		all_tools = existing_message.tool_calls
		
		print("####### Tools to be called ::: ", all_tools)
		snapshot.next
		manInTheLoop = input("Do you want to proceed (y/n): ")
		
		if manInTheLoop.lower() == "y":
			print("## Allowed")
			inputs = None  # Continue with the next step
		else:
			print("## Denied")
			break

AgentCall("Give me 1 link of youtube video of linux")
