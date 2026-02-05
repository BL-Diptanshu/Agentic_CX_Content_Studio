import uvicorn
import logging.config
import yaml
from fastapi import FastAPI
from src.routes.api_routes import router as api_router

with open('config/logging.config.yaml', 'r') as f:
    log_config = yaml.safe_load(f)
    logging.config.dictConfig(log_config)

logger = logging.getLogger(__name__)

app = FastAPI(title="Agentic CX Content Studio API")

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to Agentic CX Content Studio API"}

if __name__ == "__main__":
    logger.info("Starting Agentic CX Content Studio API...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
