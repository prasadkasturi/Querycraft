# filepath: app.py
from fastapi import FastAPI
from controllers.sql_controller import router as sql_router
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Initialize FastAPI app
app = FastAPI()

# Include the SQL controller
app.include_router(sql_router)