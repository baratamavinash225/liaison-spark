import traceback
from fastapi import APIRouter, HTTPException
from langchain_core.messages import HumanMessage
import structlog
from app.agents.workflow import create_workflow
from app.api.schemas import QueryRequest, QueryResponse

router = APIRouter()
logger = structlog.get_logger(__name__)
workflow = create_workflow()

@router.post("/generate", response_model=QueryResponse)
async def generate_code(req: QueryRequest):
    initial_state = {
        "messages": [HumanMessage(content=req.query)],
        "iteration": 0,
        "errors": ""
    }

    try:
        logger.info("generate_request_started", query=req.query)
        state_output = await workflow.ainvoke(initial_state)
        
        logger.info("generate_request_completed", iterations=state_output.get("iteration", 0))
        return QueryResponse(
            plan=state_output.get("plan", ""),
            code=state_output.get("code", ""),
            errors=state_output.get("errors", ""),
            chat_response=state_output.get("chat_response", "")
        )
    except Exception as e:
        logger.exception("generate_request_failed", error=str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))