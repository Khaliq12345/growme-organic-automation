import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes.processing import router as processing_router
from src.config.config import ENV

app = FastAPI(
    title="GrowMeOrganic API",
    description="API with required EndPoints - Structured",
    version="1.0.0",
)
# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(prefix="/api", router=processing_router, tags=["Processing"])


def start_app():
    uvicorn.run(
        "src.api.app:app",
        host="localhost",
        port=8000,
        reload=ENV != "prod",
    )
