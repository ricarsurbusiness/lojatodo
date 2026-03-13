from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.db.session import engine, Base
from app.api.v1.routes import products_routes, categories_routes
from app.models.product_model import Product
from app.models.category_model import Category


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    await engine.dispose()


app = FastAPI(
    title="Product Service",
    description="Product catalog management microservice",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(products_routes.router, prefix="/api/v1")
app.include_router(categories_routes.router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
