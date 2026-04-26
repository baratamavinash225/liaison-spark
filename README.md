# Liaison-Spark

**Liaison-Spark** is an Autonomous Big Data Analyst and Data Engineering agent. It translates natural language into highly optimized PySpark jobs using an advanced AI workflow, a Semantic Layer (RAG) powered by Weaviate, and strict Data Engineering Golden Rules.

---

## Features
- **LangGraph Agent Workflow:** A multi-node AI architecture (Router ➔ Architect ➔ Coder ➔ Reviewer) to ensure high-quality code generation.
- **RAG-Powered Semantic Layer:** Leverages Weaviate to search Data Catalogs (Hive/Glue schemas) to avoid LLM hallucinations.
- **Robust FastAPI Backend:** Asynchronous API with centralized configuration, graceful rate-limit handling, structured exception handling, strict Pydantic validation, and structured JSON logging (`structlog`).
- **Flexible LLM Support:** Built for Google Gemini (`gemini-2.5-flash`, `gemini-1.5-pro`) with seamless OpenAI fallbacks.
- **Modern Python Tooling:** Utilizes `uv` for ultra-fast dependency management and virtual environment creation.

---

## Quickstart Shortcuts
### 1. Environment Setup
```bash
# Create and activate a Python virtual environment using uv (if not already done)
cd backend && uv venv .venv && source .venv/bin/activate && cd ..

# Install all Backend & Frontend dependencies via Make
make install
```

### 2. Configuration
Create a `.env` file in the `backend` directory. You can use the following quick-template:
```ini
PROJECT_NAME="Liaison-Spark API"
VERSION="1.0.0"
DESCRIPTION="Autonomous Big Data Analyst & PySpark Generator"
APP_ENV=development
API_V1_STR=/api

# LLM Keys & Settings
LLM_MODEL="gemini-2.5-flash" # or "gemini-1.5-pro", "gpt-4o"
LLM_TEMPERATURE=0.0
EMBEDDING_MODEL="gemini-embedding-001" # or "text-embedding-004", "text-embedding-3-small"
GOOGLE_API_KEY=your_google_api_key_here
OPENAI_API_KEY=your_openai_api_key_here # Optional: For OpenAI models
OPENAI_BASE_URL=https://api.openai.com/v1 # Optional: For custom OpenAI API endpoints (e.g., Azure OpenAI, LiteLLM)

# Weaviate Vector DB (Ensure Docker is running for this)
WEAVIATE_HOST=127.0.0.1
WEAVIATE_PORT=8080
WEAVIATE_GRPC_PORT=50051
```

### 3. Start the Services
```bash
# Terminal 1: Start Weaviate Vector Database via Docker
docker-compose up -d

# Terminal 2: Run the FastAPI Backend
uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000
```

---

## API Usage

**Check System Health (Validates Weaviate Connection)**
```bash
curl -X GET "http://127.0.0.1:8000/api/health"
```

**Generate PySpark Code**
```bash
curl -X POST "http://127.0.0.1:8000/api/generate" \
     -H "Content-Type: application/json" \
     -d '{"query": "Join the users and orders tables and filter for orders placed today"}'
```