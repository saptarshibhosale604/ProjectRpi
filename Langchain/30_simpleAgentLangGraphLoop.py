import os
from typing import Annotated, TypedDict
# from dotenv import load_dotenv

from openai import OpenAI
from langchain_openai import ChatOpenAI

from langgraph.graph import StateGraph, END


# Load environment variables from .env file
# load_dotenv()

# myTestKey07 #saptarshibhosale604@gmail.com
f = open('openai_api_key.txt')
openai_key = os.environ["OPENAI_API_KEY"] = f.read().strip() 
llm_name = "gpt-3.5-turbo"
model = ChatOpenAI(api_key=openai_key, model=llm_name)


# STEP 1: Build a Basic Chatbot
from langgraph.graph.message import add_messages


class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]


def bot(state: State):
    # print(state.items())
    print(state["messages"])
    return {"messages": [model.invoke(state["messages"])]}


graph_builder = StateGraph(State)

# The first argument is the unique node name
# The second argument is the function or object that will be called whenever
# the node is used.
graph_builder.add_node("bot", bot)


# STEP 3: Add an entry point to the graph
graph_builder.set_entry_point("bot")

# STEP 4: and end point to the graph
graph_builder.set_finish_point("bot")


# STEP 5: Compile the graph
graph = graph_builder.compile()

# res = graph.invoke({"messages": ["Hello, how are you?"]})
# print(res["messages"])
from IPython.display import Image, display

try:
    img_data = graph.get_graph().draw_mermaid_png()
    
    # Save the image to a file
    img_path = 'Img/output_image01.png'  # Specify the desired output file name
    with open(img_path, 'wb') as f:
        f.write(img_data)  # Write the image data to the file

except Exception as e:
    print(f"An error occurred: {e}")

while True:
    user_input = input("User: ")
    if user_input.lower() in ["quit", "exit", "q"]:
        print("Goodbye!")
        break
    for event in graph.stream({"messages": ("user", user_input)}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)
