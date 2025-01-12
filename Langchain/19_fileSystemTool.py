
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

from tempfile import TemporaryDirectory

from langchain_community.agent_toolkits import FileManagementToolkit

# We'll make a temporary directory to avoid clutter
# ~ working_directory = TemporaryDirectory()
working_directory = "/home/rpissb/ProjectRpi/Langchain"

import os

# myTestKey07 #saptarshibhosale604@gmail.com
f = open('openai_api_key.txt')
# print("openai_api_key: ", f.read())

if not os.environ.get("OPENAI_API_KEY"):
  os.environ["OPENAI_API_KEY"] = f.read().strip() 

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-3.5-turbo", max_tokens=1000, temperature=0, max_retries=1)


from langgraph.prebuilt import create_react_agent

toolkit = FileManagementToolkit(
    # ~ root_dir=str(working_directory.name)
    root_dir=str(working_directory)
    
)  # If you don't provide a root_dir, operations will default to the current working directory
# ~ toolkit.get_tools()
tools = FileManagementToolkit(
    # ~ root_dir=str(working_directory.name),
    root_dir=working_directory
    # ~ selected_tools=["read_file", "write_file", "list_directory"],
).get_tools()

# ~ print("## ## tools:", tools)
print(tools)


agent_executor = create_react_agent(llm, tools)
# ~ example_query = "Draft an email to fake@fake.com thanking them for coffee."
# ~ example_query = "Draft an email to vedmantrabhosale@gmail.com about how should he aproach marketing for his chess class. Mail is from his brother Saptarshi Bhosale."
# ~ example_query = "list out the sorted python files in current dir and then make a file named joke02.txt and write one line joke in it"
example_query = "Tell me where is 13_agentBasic.py file or related file"

events = agent_executor.stream(
    {"messages": [("user", example_query)]},
    stream_mode="values",
)
for event in events:
    event["messages"][-1].pretty_print()
