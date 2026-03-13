from contextlib import asynccontextmanager
from fastapi import FastAPI

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

app.include_router(cart_routes.router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
