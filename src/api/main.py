"""FastAPI entry point for the 24/7 Intelligent Code Reviewer."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import submit, review, history
from src.utils.config import config
from src.utils.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="24/7 Intelligent Code Reviewer",
    description="GCP-powered automated code review — Code Kitchen S01",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(submit.router, tags=["submit"])
app.include_router(review.router, tags=["review"])
app.include_router(history.router, tags=["history"])


@app.get("/")
def root():
    return {
        "service": "24/7 Intelligent Code Reviewer",
        "status": "ok",
        "local_mode": config.LOCAL_MODE,
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8080, reload=True)
