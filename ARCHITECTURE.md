# Zero-Trust AI Policy Engine - Architecture

## System Overview

A distributed policy evaluation system using RAG (Retrieval-Augmented Generation) with a local LLM (Ollama) to automatically approve or deny policy requests based on NIST and organizational documents.

```
┌─────────────────────────────────────────────────────────────────┐
│                    Client/Frontend (React)                      │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              Go API Gateway (Port 8080)                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  POST /policy/evaluate  →  Forward to Python Backend    │  │
│  │  GET  /health           →  Service Status               │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│           Python FastAPI Backend (Port 8000)                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  POST /api/query  →  evaluate_policy()                  │  │
│  │  GET  /health     →  System Status                      │  │
│  │  GET  /docs       →  OpenAPI Documentation              │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    ┌────────┴────────────────────┐
                    ▼                             ▼
        ┌─────────────────────────┐   ┌──────────────────────┐
        │  ChromaDB (Persistent)  │   │  Ollama LLM          │
        │  Port: localhost        │   │  Port: 11434         │
        │  Path: chroma_db/       │   │  Model: mistral      │
        │                         │   │                      │
        │  Stores:                │   │  Generates:          │
        │  - NIST Embeddings      │   │  - Decisions         │
        │  - Policy Vectors       │   │  - Reasoning         │
        └────────┬────────────────┘   └──────────────────────┘
                 │
                 ▼
        ┌─────────────────────────┐
        │  Policy Documents       │
        │  Path: policies/        │
        │  Format: PDF, TXT       │
        │  Example: NIST SP 800-53
        └─────────────────────────┘
```

## Components

### 1. Go API Gateway (`go-backend/`)
- **Purpose**: HTTP reverse proxy and routing
- **Port**: 8080
- **Endpoints**:
  - `POST /policy/evaluate` - Evaluate a policy query
  - `GET /health` - Service health check
- **Features**:
  - Error handling and validation
  - Request forwarding to Python backend
  - Timeout management (30s)
  - Structured logging

### 2. Python FastAPI Backend (`python-rag/`)
- **Purpose**: Policy evaluation using RAG + LLM
- **Port**: 8000
- **Endpoints**:
  - `POST /api/query` - Evaluate policy (returns decision + reasoning)
  - `GET /health` - Service health check
  - `GET /docs` - Interactive API documentation (Swagger)
- **Components**:
  - `main.py` - FastAPI application
  - `utils.py` - RAG pipeline (ChromaDB, Ollama integration)

### 3. Vector Database (ChromaDB)
- **Type**: Persistent vector store
- **Path**: `python-rag/chroma_db/`
- **Purpose**: Store policy embeddings for RAG retrieval
- **Format**: Stored on disk (not in-memory)
- **Collection**: `policies`

### 4. LLM (Ollama)
- **Type**: Local LLM service
- **Port**: 11434
- **Model**: mistral (or configurable)
- **Purpose**: Generate policy decisions and reasoning
- **Requirement**: Running `ollama serve` in separate terminal

### 5. Policy Documents
- **Path**: `python-rag/policies/`
- **Formats**: PDF, TXT, Markdown
- **Example**: NIST SP 800-53 (Access Control policies)
- **Usage**: Ingested into ChromaDB for RAG retrieval

## Data Flow

1. **User Request**: Frontend sends policy query to Go Gateway (port 8080)
2. **Gateway**: Forwards request to Python backend (port 8000)
3. **Query Processing**:
   - FastAPI receives query
   - `build_index()` loads policies from ChromaDB
   - `query_policy()` executes RAG pipeline:
     a. Retrieve relevant policies from ChromaDB using semantic search
     b. Pass query + context to Ollama LLM
     c. LLM generates decision + reasoning
4. **Decision Logic**: Parse LLM response for "approved" keyword
5. **Response**: Return `{decision, reasoning, status}` to frontend

## Setup & Startup

### Prerequisites
```bash
# Install Ollama from https://ollama.ai
# Install Python 3.9+
# Install Go 1.21+
```

### 1. Python Environment
```bash
cd /Users/clydeshtino/zt-ai-enforcer
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Add Policy Documents
```bash
mkdir -p python-rag/policies
# Download NIST SP 800-53 PDF to policies/
```

### 3. Terminal 1: Start Ollama
```bash
ollama serve
# In another terminal:
ollama pull mistral
```

### 4. Terminal 2: Start Python Backend
```bash
cd /Users/clydeshtino/zt-ai-enforcer
source venv/bin/activate
uvicorn python-rag.main:app --reload --port 8000
```

### 5. Terminal 3: Start Go Gateway
```bash
cd go-backend
go run main.go handlers.go
```

### 6. Terminal 4: Test
```bash
# Health check
curl http://localhost:8080/health

# Policy evaluation
curl -X POST http://localhost:8080/policy/evaluate \
  -H "Content-Type: application/json" \
  -d '{"query": "Can a guest access internal resources?"}'
```

## Current Status (v0.1.0)

### ✅ Implemented
- [x] Go HTTP Gateway with error handling
- [x] Python FastAPI with RAG pipeline
- [x] ChromaDB persistent vector storage
- [x] Ollama LLM integration (mistral)
- [x] Health check endpoints
- [x] Request validation and error handling
- [x] Structured logging
- [x] OpenAPI documentation (Swagger)

### 🔄 In Progress
- [ ] Testing with NIST documents
- [ ] Fine-tune decision logic (confidence scoring)
- [ ] Integration tests

### 📋 TODO (Priority Order)

#### Phase 1: Validation & Testing
- [ ] Test with NIST SP 800-53 PDF
- [ ] Validate RAG retrieval accuracy
- [ ] Improve decision parsing (confidence scores, multiple responses)
- [ ] Add audit logging (who, what, when, why)

#### Phase 2: Security & Hardening
- [ ] Add authentication (API keys, JWT)
- [ ] Add authorization (RBAC)
- [ ] Rate limiting
- [ ] Input sanitization
- [ ] TLS/HTTPS support
- [ ] Secret management (.env)

#### Phase 3: Frontend
- [ ] React UI with policy query interface
- [ ] Decision display with reasoning
- [ ] Audit log viewer
- [ ] Policy management dashboard

#### Phase 4: Production Readiness
- [ ] Docker containerization
- [ ] Kubernetes deployment manifests
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Monitoring & alerting (Prometheus, Grafana)
- [ ] Database backup strategy
- [ ] Load testing
- [ ] Performance optimization
- [ ] Documentation (API, deployment, troubleshooting)

#### Phase 5: Advanced Features
- [ ] Multiple LLM support (GPT, Claude, etc.)
- [ ] Policy versioning & rollback
- [ ] Decision audit trail with timestamps
- [ ] Custom decision rules engine
- [ ] Webhook integrations
- [ ] Multi-tenant support

## Configuration

### Environment Variables (to add)
```bash
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=mistral
CHROMA_DB_PATH=./python-rag/chroma_db
PYTHON_API_URL=http://localhost:8000
LOG_LEVEL=INFO
```

### LLM Configuration
- **Model**: mistral (can change to other ollama models)
- **Temperature**: Default (may need tuning for consistency)
- **Context Window**: 4k tokens

## Troubleshooting

### ChromaDB Not Persisting
- Check `python-rag/chroma_db/` exists and is writable
- Verify `.gitignore` includes `python-rag/chroma_db/`

### Ollama Connection Refused
- Ensure `ollama serve` is running in Terminal 1
- Check port 11434 is accessible: `curl http://localhost:11434/api/tags`

### Python Backend Startup Errors
- Check ChromaDB path is writable
- Check `python-rag/policies/` folder exists
- Review logs for missing dependencies

### Go Gateway Can't Connect to Python
- Verify Python backend running on port 8000
- Check firewall rules
- Try: `curl http://localhost:8000/health`

## Next Steps

1. **Add NIST PDF** to `python-rag/policies/`
2. **Test end-to-end** with sample queries
3. **Iterate on decision logic** based on test results
4. **Build React frontend** (Phase 3)
5. **Deploy with Docker** (Phase 4)

## Repository Structure
```
zt-ai-enforcer/
├── python-rag/
│   ├── main.py              # FastAPI application
│   ├── utils.py             # RAG pipeline
│   ├── chroma_db/           # Persistent vector DB (gitignored)
│   ├── policies/            # Policy documents (user-provided)
│   └── __pycache__/
├── go-backend/
│   ├── main.go
│   ├── handlers.go
│   └── go.mod
├── requirements.txt         # Python dependencies
├── .gitignore
├── README.md
├── ARCHITECTURE.md          # This file
└── docker-compose.yml       # (Coming soon)
```

## Contact & Support
- Repository: https://github.com/clydeshtino/Zero-Trust-AI-Policy-Engine
- Issues: GitHub Issues
