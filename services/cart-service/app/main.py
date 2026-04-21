from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.redis_client import connect_redis, disconnect_redis
from app.api.v1.routes import cart_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_redis()
    yield
    await disconnect_redis()


app = FastAPI(
    title="Cart Service",
    description="Shopping cart microservice",
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

app.include_router(cart_routes.router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
