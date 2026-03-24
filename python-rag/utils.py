from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
import os
import logging

logger = logging.getLogger(__name__)

def get_llm():
    return Ollama(model="mistral", base_url="http://localhost:11434")

def get_embeddings():
    return OllamaEmbedding(model_name="mistral", base_url="http://localhost:11434")

def build_index():
    try:
        chroma_db_path = os.path.join(os.path.dirname(__file__), "chroma_db")
        os.makedirs(chroma_db_path, exist_ok=True)
        
        chroma_client = chromadb.PersistentClient(path=chroma_db_path)
        vector_store = ChromaVectorStore(chroma_collection=chroma_client.get_or_create_collection("policies"))
        
        Settings.embed_model = get_embeddings()
        Settings.llm = get_llm()
        
        policies_path = os.path.join(os.path.dirname(__file__), "policies")
        if os.path.exists(policies_path) and os.listdir(policies_path):
            logger.info(f"Loading policies from {policies_path}")
            documents = SimpleDirectoryReader(policies_path).load_data()
            logger.info(f"Loaded {len(documents)} documents")
            index = VectorStoreIndex.from_documents(documents, vector_store=vector_store)
            logger.info("Index built successfully")
        else:
            logger.warning(f"No policies found in {policies_path}")
            index = VectorStoreIndex.from_documents([], vector_store=vector_store)
        
        return index
    except Exception as e:
        logger.error(f"Error building index: {str(e)}", exc_info=True)
        raise

def query_policy(index, llm, query: str):
    try:
        query_engine = index.as_query_engine(llm=llm)
        response = query_engine.query(query)
        
        response_text = str(response).lower()
        decision = "approved" if "approved" in response_text else "denied"
        
        return {
            "decision": decision,
            "reasoning": str(response),
            "query": query,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error querying policy: {str(e)}", exc_info=True)
        return {
            "decision": "denied",
            "reasoning": f"Error processing request: {str(e)}",
            "query": query,
            "status": "error"
        }