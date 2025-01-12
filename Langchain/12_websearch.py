
import os

# ~ # myTestKey07 #saptarshibhosale604@gmail.com
# ~ f = open('openai_api_key.txt')
# ~ # print("openai_api_key: ", f.read())

# ~ if not os.environ.get("OPENAI_API_KEY"):
  # ~ os.environ["OPENAI_API_KEY"] = f.read().strip() 

# ~ llm = ChatOpenAI(temperature=0.0)

# export LANGSMITH_TRACING="true"
# export LANGSMITH_API_KEY="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"
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_API_KEY"] = "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"

from langchain_community.tools.tavily_search import TavilySearchResults
os.environ["TAVILY_API_KEY"] = "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"

# export TAVILY_API_KEY="..."

search = TavilySearchResults(max_results=2)
print(search.invoke("what is the weather in Pune"))
