from openai import OpenAI
from dotenv import load_dotenv
import os
import requests
import time
from langchain.document_loaders import PyPDFLoader
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA

load_dotenv()
key= os.getenv("api_key")
client = OpenAI(api_key= key)

#pdf_loader
pdf_loader= PyPDFLoader('./Data cleaning.pdf')

#now loading the pdf
documents = pdf_loader.load()

#lets move with the chunksize = 1500
chunks = CharacterTextSplitter(chunk_size=1500, chunk_overlap=300)
doc_chunks= chunks.split_documents(documents)

#using chroma db as vector store
vectordb = Chroma.from_documents(
  doc_chunks,
  embedding=OpenAIEmbeddings(),
  persist_directory='./db/'
)
vectordb.persist()

#now we will use the retrieval qa chain 
q_and_a = RetrievalQA.from_chain_type(
    llm=OpenAI(),
    retriever=vectordb.as_retriever(search_kwargs={'k': 3}), # top 3 results
    return_source_documents=True
)

def get_answer(question):
    res= q_and_a({'query': question})    
    return res['result']