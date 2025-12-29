from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.vector_stores.chroma import ChromaVectorStore
from chromadb.config import Settings as ChromaSettings
import chromadb
import os

def get_llm():
    return Ollama(model="mistral", base_url="http://localhost:11434")

def get_embeddings():
    return OllamaEmbedding(model_name="mistral", base_url="http://localhost:11434")

def build_index():
    chroma_client = chromadb.Client(ChromaSettings())
    vector_store = ChromaVectorStore(chroma_collection=chroma_client.get_or_create_collection("policies"))
    
    Settings.embed_model = get_embeddings()
    Settings.llm = get_llm()
    
    if os.path.exists("policies"):
        documents = SimpleDirectoryReader("policies").load_data()
        index = VectorStoreIndex.from_documents(documents, vector_store=vector_store)
    else:
        index = VectorStoreIndex.from_documents([], vector_store=vector_store)
    
    return index

def query_policy(index, llm, query: str):
    query_engine = index.as_query_engine(llm=llm)
    response = query_engine.query(query)
    
    decision = "approved" if "approved" in str(response).lower() else "denied"
    
    return {
        "decision": decision,
        "reasoning": str(response)
    }