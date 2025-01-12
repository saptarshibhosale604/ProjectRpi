
from langchain_google_community import GmailToolkit

from langchain_google_community.gmail.utils import (
    build_resource_service,
    get_gmail_credentials,
)

# Can review scopes here https://developers.google.com/gmail/api/auth/scopes
# For instance, readonly scope is 'https://www.googleapis.com/auth/gmail.readonly'
credentials = get_gmail_credentials(
    token_file="token.json",
    scopes=["https://mail.google.com/"],
    client_secrets_file="credentials.json",
)
api_resource = build_resource_service(credentials=credentials)
toolkit = GmailToolkit(api_resource=api_resource)

# ~ tools
# ~ toolkit = GmailToolkit()
tools = toolkit.get_tools()

# ~ print("toolkit: ", toolkit)


import os

# myTestKey07 #saptarshibhosale604@gmail.com
f = open('openai_api_key.txt')
# print("openai_api_key: ", f.read())

if not os.environ.get("OPENAI_API_KEY"):
  os.environ["OPENAI_API_KEY"] = f.read().strip() 

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")

from langgraph.prebuilt import create_react_agent
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


# ~ # Add your custom tools
# ~ tools = [get_current_time]


agent_executor = create_react_agent(llm, tools)
# ~ example_query = "Draft an email to fake@fake.com thanking them for coffee."
example_query = "Draft an email to vedmantrabhosale@gmail.com about how should he aproach marketing for his chess class. Mail is from his brother Saptarshi Bhosale."

events = agent_executor.stream(
    {"messages": [("user", example_query)]},
    stream_mode="values",
)
for event in events:
    event["messages"][-1].pretty_print()
