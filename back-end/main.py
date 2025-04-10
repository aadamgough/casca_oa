from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import analyze  # Updated import path
import os

app = FastAPI(
    title="Bank Statement Analyzer",
    description="API for analyzing bank statements and making loan decisions",
    version="1.0.0"
)

origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    f"{os.getenv('NEXT_PUBLIC_API_URL')}"
]

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Include routers
app.include_router(analyze.router, prefix="/api/v1/analyze", tags=["analyze"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Bank Statement Analyzer API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)