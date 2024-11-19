from openai import OpenAI
from dotenv import load_dotenv
import os
import requests
import time

load_dotenv()
key= os.getenv("api_key")
client = OpenAI(api_key= key)

from langchain.document_loaders import PyPDFLoader
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings

#for retrieval chain
from langchain.chains import RetrievalQA


#pdf_loader
pdf_loader= PyPDFLoader('./Data cleaning.pdf')

#now loading the pdf
documents = pdf_loader.load()


#so first of all making chunks of the document
#lets say chunksize = 1500
#and over lap characters are number of characters included in both consecutive chunks to kind of connect both chunks

chunks = CharacterTextSplitter(chunk_size=1500, chunk_overlap=300)

#making chunks of our document
doc_chunks= chunks.split_documents(documents)


vectordb = Chroma.from_documents(
  doc_chunks,
  embedding=OpenAIEmbeddings(),
  persist_directory='./db/'
)
vectordb.persist()

q_and_a = RetrievalQA.from_chain_type(
    #so llm we will be using is from openai
    llm=OpenAI(),
    #we give our vector database as retriever sources
    #k= 3 means we want to send 3 chunks from text to prompt
    retriever=vectordb.as_retriever(search_kwargs={'k': 3}),
    return_source_documents=True
)

def get_answer(question):
    #we have to pass it to the chain
    res= q_and_a({'query': question})    
    #we will just return the result
    return res['result']