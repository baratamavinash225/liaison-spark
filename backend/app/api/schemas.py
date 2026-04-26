from pydantic import BaseModel


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    plan: str = ""
    code: str = ""
    errors: str = ""
    chat_response: str = ""
