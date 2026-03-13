from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.db.session import engine, Base
from app.api.v1.routes import analytics_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    await engine.dispose()


app = FastAPI(
    title="Analytics Service",
    description="Analytics and metrics microservice",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(analytics_routes.router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
