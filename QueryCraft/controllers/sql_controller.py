from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from services.sql_service import process_sql_request, load_data_into_database

# Define the router
router = APIRouter()

# Define the request model
class PromptRequest(BaseModel):
    prompt: str = Field(..., description="The natural language query or instruction for generating SQL.", example="Generate a SELECT SQL query to select records from sample_db where which author's books are most loaned along with the titles.")
    db_name: str = Field(..., description="The name of the SQLite database file.", example="sample.db")

class LoadDataRequest(BaseModel):
    db_name: str = Field(..., description="The name of the SQLite database file.", example="sample.db")

@router.post("/generate-sql/")
async def generate_sql(request: PromptRequest):
    """
    Endpoint to generate SQL queries based on a given prompt.
    """
    # Validate the request

    try:
        response = JSONResponse(content=process_sql_request(request.prompt, request.db_name))
        # Set Cache-Control header to prevent caching
        response.headers["Cache-Control"] = "no-store"
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")
    
@router.post("/load-data/")
async def load_data(request: LoadDataRequest):
    """
    Endpoint to load data into the specified database.
    """
    try:
        msg = load_data_into_database(request.db_name)
        response = JSONResponse(content= {"message": msg})
        response.headers["Cache-Control"] = "no-store"
        return response
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"Error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")

