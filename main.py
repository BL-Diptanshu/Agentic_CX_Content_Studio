import uvicorn
import logging.config
import yaml
from dotenv import load_dotenv
from fastapi import FastAPI

# Load environment variables FIRST (Must be before importing modules that use them)
load_dotenv(override=True)

from src.routes.api_routes import router as api_router

with open('config/logging.config.yaml', 'r') as f:
    log_config = yaml.safe_load(f)
    logging.config.dictConfig(log_config)

logger = logging.getLogger(__name__)

from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(title="Agentic CX Content Studio API")

# Mount 'static' directory to serve generated images
# This enables access like http://localhost:8000/static/generated/filename.png
static_dir = os.path.join(os.getcwd(), "static")
os.makedirs(static_dir, exist_ok=True) # Ensure it exists
app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to Agentic CX Content Studio API"}

if __name__ == "__main__":
    logger.info("Starting Agentic CX Content Studio API...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
