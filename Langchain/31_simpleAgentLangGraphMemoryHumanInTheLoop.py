import os
from typing import Annotated, TypedDict
from dotenv import load_dotenv

from openai import OpenAI
from langchain_openai import ChatOpenAI

from langgraph.graph import StateGraph, END
from langchain_community.tools.tavily_search import TavilySearchResults


# Load environment variables from .env file
# load_dotenv()

def RemoveSpaces(input_string):
    # Remove spaces from the input string
    return input_string.replace(" ", "")

openai_key = "sk-proj-zP6XLa1m5gtlBcXJCaHZGmAvXEvUrP 5ATJSPBfLRdEuF-vSroLAG4V0zBdpwPz9PTXe9rM0-CgT3BlbkFJ83 AZyS7Zds5OT4G7S7MJslTok1O8P7ftX6Zz_IvdtMsy_CnjJeBoOv-o-G5t13-1Yw20ei_BwA" # myTestKey08, saptarshibhosale604@gmail.com
tavily_key = "tvly-kX76LCz C36oih0u9COcf6oa 53A47MX0g"
# result = remove_spaces(key)
# print(result)  # Output: 1234567890


os.environ["OPENAI_API_KEY"] = RemoveSpaces(openai_key)
os.environ["TAVILY_API_KEY"] = RemoveSpaces(tavily_key)


llm_name = "gpt-3.5-turbo"

# client = OpenAI(api_key=openai_key)
model = ChatOpenAI(model=llm_name)


# STEP 1: Build a Basic Chatbot
from langgraph.graph.message import add_messages


class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)

# create tools
tool = TavilySearchResults(max_results=1)
tools = [tool]
# rest = tool.invoke("What is the capital of France?")
# print(rest)

model_with_tools = model.bind_tools(tools)

# Below, implement a BasicToolNode that checks the most recent
# message in the state and calls tools if the message contains tool_calls
import json
from langchain_core.messages import ToolMessage
from langgraph.prebuilt import ToolNode, tools_condition


def bot(state: State):
    # print(state.items())
    print(state["messages"])
    return {"messages": [model_with_tools.invoke(state["messages"])]}


# instantiate the ToolNode with the tools
tool_node = ToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)  # Add the node to the graph


# The `tools_condition` function returns "tools" if the chatbot asks to use a tool, and "__end__" if
# it is fine directly responding. This conditional routing defines the main agent loop.
graph_builder.add_conditional_edges(
    "bot",
    tools_condition,
)

# The first argument is the unique node name
# The second argument is the function or object that will be called whenever
# the node is used.
graph_builder.add_node("bot", bot)


# STEP 3: Add an entry point to the graph
graph_builder.set_entry_point("bot")

# ADD MEMORY NODE
# from langgraph.checkpoint.sqlite import SqliteSaver
# memory = SqliteSaver.from_conn_string(":memory:")

from langgraph.checkpoint.memory import MemorySaver
checkpointer = MemorySaver()
# STEP 5: Compile the graph
# graph = graph_builder.compile(checkpointer=memory)
graph = graph_builder.compile(checkpointer=checkpointer, interrupt_before=["tools"])
# graph = graph_builder.compile()


from IPython.display import Image, display

try:
    img_data = graph.get_graph().draw_mermaid_png()
    
    # Save the image to a file
    img_path = 'Img/output_image03.png'  # Specify the desired output file name
    with open(img_path, 'wb') as f:
        f.write(img_data)  # Write the image data to the file
        print(f"Graph image is saved: {img_path}")

except Exception as e:
    print(f"An error occurred: {e}")


# MEMORY CODE CONTINUES ===
# Now we can run the chatbot and see how it behaves
# PICK A TRHEAD FIRST
config = {
    "configurable": {"thread_id": 1}
}  # a thread where the agent will dump its memory to

user_input = "I'm learning about astrology. Could you do some research on it for me?"

# The config is the **second positional argument** to stream() or invoke()!
events = graph.stream(
    {"messages": [("user", user_input)]}, config, stream_mode="values"
)
for event in events:
    event["messages"][-1].pretty_print()

# inspect the state
snapshot = graph.get_state(config)
next_step = snapshot.next
# this will show "action", because we've interrupted the flow before the tools node


existing_message = snapshot.values["messages"][-1]
all_tools = existing_message.tool_calls

print("tools to be called::", all_tools)



print("===>>>")  # this will show "action", because we've interrupted the flow before the tools node

interruptInput = input("wanna proceed (y/n):")

if(interruptInput == "y"):
  print("## Allowed")
  next_step
else:
  print("## Denied")

# Continue the conversation passing None to say continue - all is good
# `None` will append nothing new to the current state, letting it resume as if it had never been interrupted
events = graph.stream(None, config, stream_mode="values")
for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()

      
# user_input = "Hi there! My name is Bond. and I have been happy for 100 years"

# # The config is the **second positional argument** to stream() or invoke()!
# events = graph.stream(
#     {"messages": [("user", user_input)]}, config, stream_mode="values"
# )

# for event in events:
#     event["messages"][-1].pretty_print()


# user_input = "do you remember my name, and how long have I been happy for?"

# # The config is the **second positional argument** to stream() or invoke()!
# events = graph.stream(
#     {"messages": [("user", user_input)]}, config, stream_mode="values"
# )

# for event in events:
#     event["messages"][-1].pretty_print()


# user_input = "tell me about langchain"

# # The config is the **second positional argument** to stream() or invoke()!
# events = graph.stream(
#     {"messages": [("user", user_input)]}, config, stream_mode="values"
# )

# for event in events:
#     event["messages"][-1].pretty_print()


# snapshot = graph.get_state(config)
# print("## ##snapshot:", snapshot)


# from langchain_core.messages import BaseMessage

# while True:
#     user_input = input("User: ")
#     if user_input.lower() in ["quit", "exit", "q"]:
#         print("Goodbye!")
#         break
#     for event in graph.stream({"messages": [("user", user_input)]}):
#         for value in event.values():
#             if isinstance(value["messages"][-1], BaseMessage):
#                 print("Assistant:", value["messages"][-1].content)
