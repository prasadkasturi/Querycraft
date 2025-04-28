# filepath: app.py
from fastapi import FastAPI
from controllers.sql_controller import router as sql_router
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Initialize FastAPI app
app = FastAPI(
    title="QueryCraft API",
    description=(
        "QueryCraft API provides endpoints for managing and querying the QueryCraft database. "
        "It includes operations for loading data, generating SQL queries, and executing them."
    ),
    version="1.0.0",
    contact={
        "name": "Prasad Kasturi",
        "email": "prasad.kasturi@syngenta.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {
            "name": "Database Operations",
            "description": "Endpoints for managing the database, such as loading data.",
        },
        {
            "name": "SQL Generation",
            "description": "Endpoints for generating SQL queries using natural language prompts.",
        },
    ],
)

# Include the SQL controller
app.include_router(sql_router)