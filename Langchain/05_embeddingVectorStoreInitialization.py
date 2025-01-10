# Build a sample vectorDB
# from langchain.chat_models import ChatOpenAI
# from langchain.vectorstores import Chroma
# from langchain.document_loaders import TextLoader
# from langchain.embeddings.openai import OpenAIEmbeddings
# from langchain.text_splitter import CharacterTextSplitter
# from langchain.retrievers import ContextualCompressionRetriever
# from langchain.retrievers.document_compressors import LLMChainExtractor 


from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings.openai import OpenAIEmbeddings
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
    # PART ONE:
    # LOAD "some_data/US_Constitution in a Document object
    loader = TextLoader("./US_Constitution.txt")
    documents = loader.load()
    print("\n\n## loader ##:",loader)
    print("\n\n## documents ##:",documents)
    
    # PART TWO
    # Split the document into chunks (you choose how and what size)
    text_splitter = CharacterTextSplitter.from_tiktoken_encoder(chunk_size=500)
    docs = text_splitter.split_documents(documents)
    print("\n\n## text_splitter ##:",text_splitter)
    print("\n\n## docs ##:",docs)
    print("\n\n## docs[0] ##:",docs[0])
    
    # PART THREE
    # EMBED THE Documents (now in chunks) to a persisted ChromaDB
    embedding_function = OpenAIEmbeddings()
    db = Chroma.from_documents(docs, embedding_function,persist_directory='./US_Constitution')
    db.persist()
    print("\n\n## embedding_function ##:",embedding_function)
    print("\n\n## db ##:",db)
    
