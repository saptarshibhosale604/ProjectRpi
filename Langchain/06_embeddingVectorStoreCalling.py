
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor 

import os

# myTestKey07 #saptarshibhosale604@gmail.com
f = open('openai_api_key.txt')
# print("openai_api_key: ", f.read())

if not os.environ.get("OPENAI_API_KEY"):
  os.environ["OPENAI_API_KEY"] = f.read().strip() 


def us_constitution_helper(question):
    '''
    Takes in a question about the US Constitution and returns the most relevant
    part of the constitution. Notice it may not directly answer the actual question!
    
    Follow the steps below to fill out this function:
    '''
    
    # PART FOUR
    # return most relevent documents 
    # embedding_function = OpenAIEmbeddings()    
    # db_connection = Chroma(persist_directory='./US_Constitution',embedding_function=embedding_function)
    # print("\n\n## embedding_function ##:",embedding_function)
    # print("\n\n## db_connection ##:",db_connection)
    
    # retriever = db_connection.as_retriever()
    # # search_kwargs = {"score_threshold":0.8,"k":4}
    # # docs = retriever.get_relevant_documents(question, search_kwargs=search_kwargs)
    # # docs = retriever.get_relevant_documents(question)
    # docs = retriever.get_relevant_documents(question)

    # print("\n\n## len(docs) ##:",len(docs))
    # print("\n\n## docs[0].page_content ##:",docs[0].page_content)
    
    # PART FIVE
    # Use ChatOpenAI and ContextualCompressionRetriever to return the most
    # relevant part of the documents.

    llm = ChatOpenAI(temperature=0)
    compressor = LLMChainExtractor.from_llm(llm)
    embedding_function = OpenAIEmbeddings()    
    db_connection = Chroma(persist_directory='./US_Constitution',embedding_function=embedding_function)

    compression_retriever = ContextualCompressionRetriever(base_compressor=compressor, 
                                                           base_retriever=db_connection.as_retriever())

    compressed_docs = compression_retriever.get_relevant_documents(question)

    print(compressed_docs[0].page_content)
    
us_constitution_helper("What was the 1st amendment?")
