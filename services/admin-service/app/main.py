from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.api.v1.routes import admin_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="Admin Service",
    description="Admin dashboard and management microservice",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(admin_routes.router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
