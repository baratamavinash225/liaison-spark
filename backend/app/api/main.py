import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()
from app.agents.workflow import create_workflow

app = FastAPI(title="Liaison-Spark API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

workflow = create_workflow()

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    plan: str
    code: str
    errors: str

@app.post("/api/generate", response_model=QueryResponse)
def generate_code(req: QueryRequest):
    initial_state = {
        "messages": [HumanMessage(content=req.query)],
        "iteration": 0,
        "errors": ""
    }

    try:
        state_output = workflow.invoke(initial_state)
        return QueryResponse(
            plan=state_output.get("plan", ""),
            code=state_output.get("code", ""),
            errors=state_output.get("errors", "")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
