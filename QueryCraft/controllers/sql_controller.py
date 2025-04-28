from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.sql_service import process_sql_request

# Define the router
router = APIRouter()

# Define the request model
class PromptRequest(BaseModel):
    prompt: str

@router.post("/generate-sql/")
async def generate_sql(request: PromptRequest):
    """
    Endpoint to generate SQL queries based on a given prompt.
    """
    try:
        return process_sql_request(request.prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")