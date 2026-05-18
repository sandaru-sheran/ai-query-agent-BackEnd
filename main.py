from fastapi import FastAPI
from app.controller.queryController import router as query_router

app = FastAPI(title="AI Query Agent API")

# Include routers
app.include_router(query_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to AI Query Agent API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
