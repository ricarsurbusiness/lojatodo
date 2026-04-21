from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

# CORS middleware - allow frontend origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(notifications_routes.router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
