from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import Base, engine
from backend import models
from backend.routes.github import router as github_router
from backend.routes.review import router as review_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Multi-Agent PR Review System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(github_router)
app.include_router(review_router)


@app.get("/")
def root():
    return {
        "status": "running",
        "service": "Multi-Agent PR Review System",
    }
