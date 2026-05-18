from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.controller.queryController import router as query_router

app = FastAPI(title="AI Query Agent API")

origins = [
    "http://localhost:3000",      # React local development port
    "http://127.0.0.1:3000",    # Alternative local address
]

# 3. Add the middleware to your FastAPI app instance
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,           # Allows requests from your React app
    allow_credentials=True,
    allow_methods=["*"],             # Allows GET, POST, DELETE, OPTIONS, etc.
    allow_headers=["*"],             # Allows all custom headers (Content-Type, X-Requested-With, etc.)
)

# Include routers
app.include_router(query_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to AI Query Agent API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
