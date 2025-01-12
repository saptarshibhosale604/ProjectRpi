
# ~ from langchain_google_community import GmailToolkit

# ~ from langchain_google_community.gmail.utils import (
    # ~ build_resource_service,
    # ~ get_gmail_credentials,
# ~ )

# Can review scopes here https://developers.google.com/gmail/api/auth/scopes
# For instance, readonly scope is 'https://www.googleapis.com/auth/gmail.readonly'
# ~ credentials = get_gmail_credentials(
    # ~ token_file="token.json",
    # ~ scopes=["https://mail.google.com/"],
    # ~ client_secrets_file="credentials.json",
# ~ )
# ~ api_resource = build_resource_service(credentials=credentials)
# ~ toolkit = GmailToolkit(api_resource=api_resource)

# ~ tools
# ~ toolkit = GmailToolkit()
# ~ tools = toolkit.get_tools()

# ~ print("toolkit: ", toolkit)

# ~ from tempfile import TemporaryDirectory

# ~ from langchain_community.agent_toolkits import FileManagementToolkit

from langchain_community.agent_toolkits import PlayWrightBrowserToolkit

from langchain_community.tools.playwright.utils import (
    create_async_playwright_browser,  # A synchronous browser is available, though it isn't compatible with jupyter.\n",	  },
)

# This import is required only for jupyter notebooks, since they have their own eventloop
import nest_asyncio

nest_asyncio.apply()
# ~ async_browser = create_async_playwright_browser(True, ["firefox.launch"])
async_browser = create_async_playwright_browser()

# ~ print("## ## async_browser:", async_browser)

toolkit = PlayWrightBrowserToolkit.from_browser(async_browser=async_browser)
tools = toolkit.get_tools()

# ~ print("## ## tools:", tools)


tools_by_name = {tool.name: tool for tool in tools}
navigate_tool = tools_by_name["navigate_browser"]
get_elements_tool = tools_by_name["get_elements"]

import asyncio

async def main02():
    print("main02 running")
    
    # ~ await navigate_tool.arun(
    result = await navigate_tool.arun(
    	{"url": "https://google.com"})
    	
    # The browser is shared across tools, so the agent can interact in a stateful manner
    result02 = await get_elements_tool.arun(
        {"selector": ".container__headline", "attributes": ["innerText"]}
    )
    
    print("## ## result:", result)
    
    print("## ## result02:", result02)
    # ~ {"url": "https://web.archive.org/web/20230428133211/https://cnn.com/world"})
    # ~ )
    
    print("main02 done")

# ~ asyncio.run(main02())
    
# ~ def main03():
	# ~ await navigate_tool.arun(
    	# ~ {"url": "https://web.archive.org/web/20230428133211/https://cnn.com/world"})

# ~ main03()
# ~ result = await navigate_tool.arun(
    	# ~ {"url": "https://web.archive.org/web/20230428133211/https://cnn.com/world"})
# ~ print(result)
# Run the async function

# ~ await navigate_tool.arun(
    # ~ {"url": "https://web.archive.org/web/20230428133211/https://cnn.com/world"}
# ~ )



# ~ print(tools)
# ~ # We'll make a temporary directory to avoid clutter
# ~ working_directory = TemporaryDirectory()
# ~ working_directory = "/home/rpissb/ProjectRpi/Langchain"

import os

# myTestKey07 #saptarshibhosale604@gmail.com
f = open('openai_api_key.txt')
# print("openai_api_key: ", f.read())

if not os.environ.get("OPENAI_API_KEY"):
  os.environ["OPENAI_API_KEY"] = f.read().strip() 

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-3.5-turbo", max_tokens=1000, temperature=0, max_retries=1)


from langchain.agents import AgentType, initialize_agent



agent_chain = initialize_agent(
    tools,
    llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
)



# ~ print(result)

async def main02():
    print("main02 running")
    
    result = await agent_chain.arun("summaries langchain.com in a paragraph")

    print("## ## result:", result)
    
    # ~ print("## ## result02:", result02)
  
    print("main02 done")

asyncio.run(main02())




# ~ from langgraph.prebuilt import create_react_agent

# ~ toolkit = FileManagementToolkit(
    # ~ root_dir=str(working_directory.name)
    # ~ root_dir=str(working_directory)
    
# ~ )  # If you don't provide a root_dir, operations will default to the current working directory
# ~ toolkit.get_tools()
# ~ tools = FileManagementToolkit(
    # ~ root_dir=str(working_directory.name),
    # ~ root_dir=working_directory,
    # ~ selected_tools=["read_file", "write_file", "list_directory"],
# ~ ).get_tools()

# ~ tools

# ~ from langchain_core.tools import tool

# ~ @tool
# ~ def get_current_time() -> str:
    # ~ """
    # ~ Returns the current time in hh:mm format.
    # ~ """
    # ~ return datetime.now().strftime("%H:%M")

# ~ @tool
# ~ def get_current_date() -> str:
    # ~ """
    # ~ Returns the current date in dd,mm,yyyy format.
    # ~ """
    # ~ return datetime.now().strftime("%d,%m,%Y")


# Add your custom tools
# ~ tools = [get_current_time]


# ~ agent_executor = create_react_agent(llm, tools)
# ~ example_query = "Draft an email to fake@fake.com thanking them for coffee."
# ~ example_query = "Draft an email to vedmantrabhosale@gmail.com about how should he aproach marketing for his chess class. Mail is from his brother Saptarshi Bhosale."
# ~ example_query = "list out the sorted python files in current dir and then make a file named joke02.txt and write one line joke in it"

# ~ events = agent_executor.stream(
    # ~ {"messages": [("user", example_query)]},
    # ~ stream_mode="values",
# ~ )
# ~ for event in events:
    # ~ event["messages"][-1].pretty_print()
