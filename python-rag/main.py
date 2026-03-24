from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from utils import build_index, get_llm, query_policy
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Zero-Trust AI Policy Engine",
    description="RAG-based policy evaluation system using Ollama and ChromaDB",
    version="0.1.0"
)

try:
    index = build_index()
    llm = get_llm()
    logger.info("System initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize system: {str(e)}")
    raise

class Query(BaseModel):
    query: str

class PolicyResponse(BaseModel):
    decision: str
    reasoning: str
    query: str
    status: str

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Zero-Trust AI Policy Engine"
    }

@app.post("/api/query", response_model=PolicyResponse)
def evaluate_policy(q: Query):
    if not q.query or q.query.strip() == "":
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    try:
        result = query_policy(index, llm, q.query)
        return result
    except Exception as e:
        logger.error(f"Error in policy evaluation: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")