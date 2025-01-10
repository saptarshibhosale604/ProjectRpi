from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.chains.question_answering import load_qa_chain
import os

# myTestKey07 #saptarshibhosale604@gmail.com
f = open('openai_api_key.txt')
# print("openai_api_key: ", f.read())

if not os.environ.get("OPENAI_API_KEY"):
  os.environ["OPENAI_API_KEY"] = f.read().strip() 

embedding_function = OpenAIEmbeddings()
db_connection = Chroma(persist_directory='./US_Constitution/',embedding_function=embedding_function)

llm = ChatOpenAI(temperature=0)

# without returning context file
chain = load_qa_chain(llm,chain_type='stuff')
question = "What is the 15th amendment?"
docs = db_connection.similarity_search(question)
result = chain.run(input_documents=docs,question=question)
print("\n\n## result ##:",result)

# with returning context file
chain = load_qa_with_sources_chain(llm,chain_type='stuff')
query = "What is the 14th amendment?"
docs = db_connection.similarity_search(query)
result02 = chain.run(input_documents=docs,question=query)
print("\n\n## result02 ##:",result02)


