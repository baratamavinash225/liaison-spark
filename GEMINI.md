# 🧠 Liaison-Spark: AI Assistant Brain Dump

**Hello Gemini / AI Assistant!** 
If you are reading this, you are assisting with the development of **Liaison-Spark**, an Autonomous Big Data Analyst and Data Engineering agent. 

Please read this document carefully before suggesting code modifications. It outlines the architectural boundaries, tech stack, and design principles of the project.

---

## 🚀 Project Overview
Liaison-Spark acts as an autonomous assistant that translates natural language into highly optimized PySpark jobs. Instead of feeding the LLM an entire contextless Data Catalog, it utilizes a **Semantic Layer (RAG)** combined with **Hardcoded Golden Rules** to ensure the generated PySpark code uses predicate pushdowns, broadcast joins, and avoids full table scans.

## 🛠️ Core Tech Stack
- **Backend Framework:** FastAPI (Asynchronous)
- **AI/Agent Framework:** LangGraph & LangChain (`langchain-google-genai`, `langchain-openai`)
- **Vector Database:** Weaviate (Local Docker container via `langchain-weaviate`)
- **Observability:** `structlog` (Structured JSON logging) & `OpenTelemetry` (Tracing)
- **LLMs:** Google Gemini (`gemini-2.5-flash` / `gemini-1.5-pro`) & OpenAI fallback.
- **Embeddings:** Google `text-embedding-004` (or `gemini-embedding-001`)
- **Frontend:** React (JSX)
- **PackageManager:** uv

---

## 🏗️ Architecture & Directory Structure

The backend follows strict **Separation of Concerns (SoC)** and **Single Responsibility Principle (SRP)**.

```text
backend/
├── app/
│   ├── agents/                  # LangGraph Workflow & State
│   │   ├── nodes/               # Individual LangGraph Node Classes
│   │   │   ├── base.py          # BaseNode abstract class
│   │   │   ├── router.py        # Intent classification (Structured Output)
│   │   │   ├── architect.py     # Plans the execution
│   │   │   ├── coder.py         # Writes the PySpark code
│   │   │   ├── reviewer.py      # QA checks the code against constraints
│   │   │   └── chat.py          # Conversational fallback
│   │   ├── state.py             # AgentState TypedDict definition
│   │   └── workflow.py          # StateGraph routing logic and conditional edges
│   ├── api/                     # FastAPI Layer
│   │   ├── main.py              # App initialization and Lifespan
│   │   ├── routes.py            # API endpoints (e.g., /api/generate)
│   │   └── schemas.py           # Pydantic request/response schemas
│   ├── core/                    # Observability & Config
│   │   ├── logging/logging.py   # structlog configuration
│   │   └── telemetry/telemetry.py # OpenTelemetry & LangChain Instrumentor
│   ├── ingestion/               # ETL pipelines for the Vector DB
│   │   └── metadata_harvester.py# Scans JSONs and uploads schemas to Weaviate
│   ├── rag/                     # Retrieval-Augmented Generation
│   │   └── semantic_layer.py    # Weaviate Vector Store integration & Golden Rules
│   └── services/                # External Service Connections (Singletons)
│       ├── llm_service.py       # Centralized LLM & Embedding instantiation
│       └── weaviate_service.py  # Weaviate DB connection manager
```

---

## 🤖 LangGraph Workflow Execution
1. **`router`**: Uses `with_structured_output` (Pydantic) to determine user intent. Emits `next_node` and `routing_reasoning`.
2. **`architect`**: Consults the `semantic_layer` to fetch relevant Hive/Glue table schemas via Vector Search, then generates a step-by-step query execution plan.
3. **`coder`**: Takes the `architect`'s plan and the `semantic_layer` schemas to write pure PySpark code.
4. **`reviewer`**: QA checks the generated code against the **Golden Rules**. If it fails, it increments the `iteration` state and routes back to the `coder` with error context. If it succeeds, it outputs `APPROVED`.
5. **`chat_node`**: Handles standard conversational replies (hello, who are you).

---

## 📜 AI Contributor Rules (How to write code for this project)

When generating code for Liaison-Spark, STRICTLY adhere to the following rules:

1. **Async by Default:** All LangGraph nodes, API routes, and LLM invocations MUST use `async def` and `await ... .ainvoke()`. Do not block the FastAPI event loop.
2. **Dependency Injection & Singletons:** Do NOT instantiate `ChatOpenAI`, `ChatGoogleGenerativeAI`, or `WeaviateClient` directly in feature modules. ALWAYS import and use `llm_service` and `weaviate_service` from `app/services/`.
3. **Structured Output:** When prompting an LLM to make a definitive decision (like routing or categorizing), use LangChain's `.with_structured_output(PydanticModel)`. Include a `reasoning` field in the Pydantic schema to force Chain-of-Thought.
4. **Observability First:** Use `import structlog; logger = structlog.get_logger(__name__)` for logging. Pass contextual data as kwargs (e.g., `logger.info("event_name", query=user_query, iteration=2)`). Do NOT use Python's standard `print()` or `logging.info()`.
5. **Message Formatting:** When sending prompts to LLMs, explicitly separate instructions using `SystemMessage(content=...)` and data using `HumanMessage(content=...)`. Do not bundle instructions into the HumanMessage.
6. **Semantic Layer Filtering:** The `SemanticLayer.get_context()` method accepts a `database_schemas: List[str]` argument. Ensure the AI architect extracts this list if the user mentions specific databases (e.g., HR, Finance) to enable Hybrid Vector Filtering in Weaviate.

---

## 📝 Context & State Reference

**AgentState keys (`app/agents/state.py`):**
- `messages`: Sequence[BaseMessage]
- `plan`: str
- `code`: str
- `errors`: str
- `iteration`: int
- `next_node`: str (Used by the router)
- `routing_reasoning`: str
- `chat_response`: str

**Data Engineering Golden Rules (`semantic_layer.py`):**
1. PREDICATE PUSHDOWN: Always filter by partition columns BEFORE joining.
2. BROADCAST JOINS: Use F.broadcast() for dimension tables under 10MB.
3. COLUMN PRUNING: Select only required columns.
4. AVOID SHUFFLES: Minimize distinct() or groupBy() without filtering.