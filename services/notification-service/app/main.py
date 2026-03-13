from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.api.v1.routes import notifications_routes
from app.db.session import engine, Base
from app.models.notification_model import Notification
from app.consumers.event_consumer import event_consumer


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    event_consumer.start_in_background(
        queue_name="notification_events",
        routing_keys=[
            "order.created",
            "order.shipped",
            "payment.completed",
            "payment.failed",
        ],
    )

    yield

    event_consumer.close()
    await engine.dispose()


app = FastAPI(
    title="Notification Service",
    description="Notification management microservice with email and event handling",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(notifications_routes.router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
