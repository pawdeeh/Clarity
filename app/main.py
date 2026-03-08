# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import document_routes, api_auth, asset_routes
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Clarity Documentation Platform",
    description="Technical documentation platform with versioning, collaboration, and advanced content features",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, configure specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint for load balancers and monitoring"""
    return {"status": "healthy", "service": "clarity"}

# Include routes
app.include_router(api_auth.router)
app.include_router(document_routes.router)
app.include_router(asset_routes.router)

# Root endpoint
@app.get("/", tags=["root"])
async def root():
    return {
        "message": "Clarity Documentation Platform",
        "docs": "/docs",
        "redoc": "/redoc",
        "api": "/api",
        "auth": "/api/auth"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)