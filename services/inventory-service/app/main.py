from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.session import engine, Base
from app.api.v1.routes import inventory_routes
from app.models.inventory_model import Inventory, InventoryReservation


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    await engine.dispose()


app = FastAPI(
    title="Inventory Service",
    description="Inventory management microservice",
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

app.include_router(inventory_routes.router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
