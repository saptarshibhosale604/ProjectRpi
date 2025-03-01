##Langchain template
# includes OPEN ai api key, agent, terminal/Shell tool, 
# UserInput

#### langgraph, man in the loop, Getting end of the graph
## Shell tool and agent

# ~ from langchain.agents import AgentType, initialize_agent
from langchain_openai import ChatOpenAI

import os

# Load OpenAI API key
f = open('API_KEY_OPENAI.txt')
if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = f.read().strip()

llm = ChatOpenAI(model="gpt-3.5-turbo", max_tokens=1000, temperature=0, max_retries=1)

from langgraph.prebuilt import create_react_agent
from langchain_community.tools import ShellTool



# Initialize tools

toolShell = ShellTool(ask_human_input=False, verbose=True)
toolShell.description = toolShell.description + f"args {toolShell.args}".replace("{", "{{").replace("}", "}}")
toolShell.description += f" Note: This tool should only be called if the input explicitly includes the phrase 'my pc'"



# Custome cron job tool
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage

CREATE_CRONJOB_PROMPT = '''From the give user input, Returns only CRON JOB output, Do not include any other text.
from user input parse the following data:
minute,
hour,
title,
message.
Make cron job with following format:
<minute> <hour> * * * echo "<title> - <message>" >> /var/log/notify.log 2>&1 '''

def UpdateFile(data, filename):
	with open(filename, 'a') as file:  # Open the file in append mode
		file.write(str(data) + '\n')  # Write the data followed by a newline

@tool
def toolSetRemainder(userInput :str) -> str:
	'''Returns the CRON JOB format for remainder setting.
	Expects an input with the start 'set remainder'.
	'''
	userInput = f"user input = '{userInput}'"
	messages = [
		SystemMessage(content=CREATE_CRONJOB_PROMPT),
		HumanMessage(content=userInput)
	]

	response = llm.invoke(messages)
	
	llmResponce = response.content
	UpdateFile(llmResponce, "mycron")
	return {"Cron job": llmResponce}



#toolsAdvance =  [toolShell  + toolkitSQL_DB] + toolGmail               	# Need for human in loop
toolsAdvance =  [toolShell] + [toolSetRemainder]   # Need for human in loop
#toolsBasic = [toolYoutube, toolWebSearch]                  # No need for human in loop

tools = toolsAdvance # + toolsBasic




# ~ userInput = "Tell me where is 13_agentBasic.py file"
# ~ userInput = "step 1: Tell me where is 13_agentBasic.py file and step 2: then find other python files from same folder"
# ~ userInput = "start a timer for 10 sec and after timer over play alarm clock sound to notify"
#userInput = "play a blue eyes youtube video on firefox"
# ~ userInput = "find the location of lanchain dir and then Give me the list of python files from that langchain directory"
#userInput = "find the location of 'README.txt' file"
userInput = "set reminder at 14:30 for Meeting with team with message Don't forget to bring the report"

from langgraph.checkpoint.memory import MemorySaver
agent_executor = create_react_agent(llm, tools, interrupt_before=["tools"])

# ~ events = agent_executor.stream(
    # ~ {"messages": [("user", userInput)]},
    # ~ stream_mode="values",
    
# ~ )

graph = create_react_agent(
     llm, tools, interrupt_before=["tools"], checkpointer=MemorySaver()
)
config = {"configurable": {"thread_id": "thread-1"}}

def print_stream(graph, inputs, config):
    for s in graph.stream(inputs, config, stream_mode="values"):
        message = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()

# ~ inputs = {"messages": [("user", userInput)]}
# ~ print_stream(graph, inputs, config)
# ~ snapshot = graph.get_state(config)

# ~ print("#######Next step: ", snapshot.next)
# ~ manInTheLoop = input("Do you wann proceed(y/n):")

# ~ if(manInTheLoop == "y"):
	# ~ print("## Allowed")
	# ~ print_stream(graph, None, config)
# ~ else:
	# ~ print("## Denied")
	

# Main loop to process the graph
inputs = {"messages": [("user", userInput)]}  # Replace with actual input
loopCounter = 0

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

    print("####### Next step: ", snapshot.next)
    manInTheLoop = input("Do you want to proceed (y/n): ")

    if manInTheLoop.lower() == "y":
        print("## Allowed")
        inputs = None  # Continue with the next step
    else:
        print("## Denied")
        break

# ~ for event in events:
    # ~ event["messages"][-1].pretty_print()

# ~ agent_executor = create_react_agent(llm, tools)

# ~ events = agent_executor.stream(
    # ~ {"messages": [("user", userInput)]},
    # ~ stream_mode="values",
# ~ )

# ~ for event in events:
    # ~ messages = event.get("messages", [])
    # ~ for message in messages:
        # ~ if message["role"] == "ai":
            # ~ # Check if the AI message includes tool call information
            # ~ if "thought" in message:
                # ~ print("================================= Thought =================================")
                # ~ print(message["thought"])
            # ~ if "action" in message:
                # ~ print("================================== Action ==================================")
                # ~ print(message["action"])
            # ~ if "action_input" in message:
                # ~ print("================================= Action Input ==============================")
                # ~ print(message["action_input"])
        # ~ message.pretty_print()  # This will still display the original output



# ~ from langchain.agents import load_tools, initialize_agent, AgentType



# ~ agent = initialize_agent(tools, llm, agent = AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)

# ~ result = agent.invoke(userInput)

# ~ print(result)
