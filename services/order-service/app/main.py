from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.api.v1.routes import orders_routes
from app.db.session import engine, Base
from app.models.order_model import Order
from app.models.order_item_model import OrderItem


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()


app = FastAPI(
    title="Order Service",
    description="Order management microservice",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(orders_routes.router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
