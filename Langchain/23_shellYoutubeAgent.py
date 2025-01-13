#### langgraph, man in the loop, Getting end of the graph



# ~ ## Running basic shell tool

# ~ from langchain_community.tools import ShellTool

# ~ shell_tool = ShellTool()

# ~ result = shell_tool.run({"commands": ["echo 'Hello World!'", "time"]})
# ~ result = shell_tool.run({"commands": ["bash -c \"echo 'Hello World!'\"", "bash -c time"]})
# ~ result = shell_tool.run({"commands": ["zsh -c \"echo 'Hello World!'\"", "zsh -c time"]})

# ~ print(result)

## Shell tool and agent

# ~ from langchain.agents import AgentType, initialize_agent
from langchain_openai import ChatOpenAI

import os

# Load OpenAI API key
f = open('openai_api_key.txt')
if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = f.read().strip()

llm = ChatOpenAI(model="gpt-3.5-turbo", max_tokens=1000, temperature=0, max_retries=1)

from langgraph.prebuilt import create_react_agent
from langchain_community.tools import ShellTool

# Initialize tools
tools = ShellTool(ask_human_input=True, verbose=True)
shellTool = ShellTool(ask_human_input=False, verbose=True)
shellTool.description = shellTool.description + f"args {shellTool.args}".replace("{", "{{").replace("}", "}}")

tools =  [shellTool]
# ~ tools01 = ShellTool(ask_human_input=False, verbose=True)







from langchain_community.tools import YouTubeSearchTool

# ~ tools += YouTubeSearchTool()
tools += [YouTubeSearchTool()]




# ~ print("tools:", tools)

# ~ userInput = "Tell me where is 13_agentBasic.py file in my pc"
# ~ userInput = "step 1: Tell me where is 13_agentBasic.py file and step 2: then find other python files from same folder"
# ~ userInput = "start a timer for 10 sec and after timer over play alarm clock sound to notify"
# ~ userInput = "play blue eyes by honey singh youtube video on the firefox app"
# ~ userInput = "play blue eyes by honey singh youtube video using firefox cmd in background"
# ~ userInput = "play doku punjabi song youtube video using firefox cmd in background"
# ~ userInput = "start the stopwatch in terminal"
# ~ userInput = "start the timer for 5 sec and notify with alarm clock sound"
userInput = "tell me storage information"

# ~ userInput = "get link for blue eyes by honey singh youtube video and then run the 1st link using only firefox cmd"
# ~ userInput = "play blue eyes by honey singh youtube video"
# ~ userInput = "find the location of lanchain dir and then Give me the list of python files from that langchain directory"
# ~ userInput = "find the location of 'Lanchain' dir"


print("## ## tools:", tools)


from langgraph.checkpoint.memory import MemorySaver
# ~ agent_executor = create_react_agent(llm, tools, interrupt_before=["tools01"])
# ~ agent_executor = create_react_agent(llm, tools)

# ~ events = agent_executor.stream(
    # ~ {"messages": [("user", userInput)]},
    # ~ stream_mode="values",
    
# ~ )

graph = create_react_agent(
     llm, tools, interrupt_before=["tools"], checkpointer=MemorySaver()
     # ~ llm, tools, checkpointer=MemorySaver()
     
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
