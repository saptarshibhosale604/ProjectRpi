
import os

# myTestKey07 #saptarshibhosale604@gmail.com
f = open('openai_api_key.txt')
# print("openai_api_key: ", f.read())

if not os.environ.get("OPENAI_API_KEY"):
  os.environ["OPENAI_API_KEY"] = f.read().strip() 


# First we initialize the model we want to use.
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4o", temperature=0, verbose=True)


# For this tutorial we will use custom tool that returns pre-defined values for weather in two cities (NYC & SF)

from typing import Literal

from langchain_core.tools import tool


@tool
def get_weather(city: Literal["nyc", "sf"]):
    """Use this to get weather information."""
    if city == "nyc":
        return "It might be cloudy in nyc"
    elif city == "sf":
        return "It's always sunny in sf"
    else:
        raise AssertionError("Unknown city")


@tool
def coolest_guy(text :str) -> str:
	'''Returns the name of the coolest person in the universe.
	Expects an input of an empty string '' and returns the 
	name of the coolest person in the universe
	'''
	return "Saptarshi Bhosale"
	
# ~ tools = [get_weather, coolest_guy, 'wikipedia','llm-math']

from langchain.agents import load_tools
# ~ from langchain_community.agent_toolkits.load_tools import load_tools

# Load pre-defined tools
loaded_tools = load_tools(['wikipedia', 'llm-math'], llm=model)

# Add your custom tools
tools = loaded_tools + [get_weather, coolest_guy]

# ~ print("\n\n## tools ##:", tools)

# Define the graph

from langgraph.prebuilt import create_react_agent

graph = create_react_agent(model, tools=tools)


from IPython.display import Image, display

try:
    img_data = graph.get_graph().draw_mermaid_png()
    
    # Save the image to a file
    img_path = 'Img/output_image01.png'  # Specify the desired output file name
    with open(img_path, 'wb') as f:
        f.write(img_data)  # Write the image data to the file

except Exception as e:
    print(f"An error occurred: {e}")

# ~ from IPython.display import Image, display

# ~ print("\n\n## display(Image(graph. ##:")


# ~ display(Image(graph.get_graph().draw_mermaid_png()))


def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()

userInput = "what's the weather in new york city and who's the coolest person in the Universe"

inputs = {"messages": [("user", userInput)]}
print_stream(graph.stream(inputs, stream_mode="values"))





# ~ print("\n\n## destination_chains ##:", destination_chains)
