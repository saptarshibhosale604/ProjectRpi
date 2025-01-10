import time
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain.prompts import (
    ChatPromptTemplate,
    PromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)

## ## Initialization
# myTestKey07 #saptarshibhosale604@gmail.com
f = open('openai_api_key.txt')
# print("openai_api_key: ", f.read())

if not os.environ.get("OPENAI_API_KEY"):
  os.environ["OPENAI_API_KEY"] = f.read().strip() 

chat = ChatOpenAI()


## ## Method 01, simple template

# system_template="You are an AI recipe assistant that specializes in {dietary_preference} dishes that can be prepared in {cooking_time}."
# system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)

# human_template="{recipe_request}"
# human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

# chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

# print("inputVars:", chat_prompt.input_variables)

# # get a chat completion from the formatted messages
# request = chat_prompt.format_prompt(cooking_time="5 min", dietary_preference="veg", recipe_request="maggie").to_messages()

# print("request:", request)

# result = chat.invoke(request)

# print("result:::::", result)

## ## Method 02, Few shot template
template = "You are a helpful assistant that translates complex legal terms into plain and understandable terms."
system_message_prompt = SystemMessagePromptTemplate.from_template(template)

legal_text = "The provisions herein shall be severable, and if any provision or portion thereof is deemed invalid, illegal, or unenforceable by a court of competent jurisdiction, the remaining provisions or portions thereof shall remain in full force and effect to the maximum extent permitted by law."
example_input_one = HumanMessagePromptTemplate.from_template(legal_text)

plain_text = "The rules in this agreement can be separated. If a court decides that one rule or part of it is not valid, illegal, or cannot be enforced, the other rules will still apply and be enforced as much as they can under the law."
example_output_one = AIMessagePromptTemplate.from_template(plain_text)

human_template = "{legal_text}"
human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

chat_prompt = ChatPromptTemplate.from_messages(
    [system_message_prompt, example_input_one, example_output_one, human_message_prompt]
)

some_example_text = "The grantor, being the fee simple owner of the real property herein described, conveys and warrants to the grantee, his heirs and assigns, all of the grantor's right, title, and interest in and to the said property, subject to all existing encumbrances, liens, and easements, as recorded in the official records of the county, and any applicable covenants, conditions, and restrictions affecting the property, in consideration of the sum of [purchase price] paid by the grantee."
request = chat_prompt.format_prompt(legal_text=some_example_text).to_messages()

result = chat.invoke(request)

print(result.content)
