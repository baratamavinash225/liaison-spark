import traceback
from fastapi import APIRouter, HTTPException
from langchain_core.messages import HumanMessage
import structlog
from app.agents.workflow import create_workflow
from app.api.schemas import QueryRequest, QueryResponse
from app.core.exceptions.exceptions import LLMRateLimitException

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
    except LLMRateLimitException as e:
        logger.warning("rate_limit_hit", error=str(e))
        return QueryResponse(
            chat_response="""I'm currently receiving too many requests and hit my API rate limit. 
            Please try again in about 15 seconds!"""
        )
    except Exception as e:
        error_msg = str(e)
        
        # Map third-party API rate limits to our custom exception logic
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            logger.warning("rate_limit_hit", error=error_msg)
            return QueryResponse(
                chat_response="""I'm currently receiving too many requests and hit my API rate limit. 
                Please try again in about 15 seconds!"""
            )
            
        logger.exception("generate_request_failed", error=error_msg)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=error_msg)