from openai import OpenAI
from langchain.document_loaders import PyPDFLoader
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains.question_answering import load_qa_chain
from langchain.chat_models import ChatOpenAI

# Initialize persistent RAG components
class RAGChatbot:
    def __init__(self, file_path, api_key):
        self.api_key = api_key
        client = OpenAI(api_key=api_key)
        
        # Loading and spliting the PDF document into chunks (so that we can embed them)
        pdf_loader = PyPDFLoader(file_path)
        documents = pdf_loader.load()
        chunks = CharacterTextSplitter(chunk_size=1500, chunk_overlap=300)
        doc_chunks = chunks.split_documents(documents)
        
        #we will use chroma to store the embeddings of the document chunks for this task
        self.vectordb = Chroma.from_documents(
            doc_chunks,
            embedding=OpenAIEmbeddings(),
            persist_directory='./db/'
        )
        self.vectordb.persist()

        self.llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.5)
        self.chain = load_qa_chain(self.llm, chain_type="stuff")
    
    # Method to ask a question and get an answer from the rag chatbot
    def ask(self, question):
        retriever = self.vectordb.as_retriever(search_kwargs={"k": 3})
        context = retriever.get_relevant_documents(question)
        answer = self.chain({"input_documents": context, "question": question}, return_only_outputs=True)['output_text']
        return answer

# Testing locally
# api_key = ""
# file_path = "pdf_files/Usman-Yaqoob_AI-ML-DS.pdf"
# rag_chatbot = RAGChatbot(file_path, api_key)
# question1 = "What are the main skills mentioned in the document?"
# print(rag_chatbot.ask(question1))

