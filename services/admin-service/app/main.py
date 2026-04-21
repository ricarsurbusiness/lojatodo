from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

# CORS middleware - allow frontend origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_routes.router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
