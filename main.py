import uvicorn
from fastapi import FastAPI
from src.routes.api_routes import router as api_router
# from src.core.database import Base, engine # Tables are already created manually

app = FastAPI(title="Agentic CX Content Studio API")

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to Agentic CX Content Studio API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
