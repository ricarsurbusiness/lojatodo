from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

# CORS middleware - allow frontend origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products_routes.router, prefix="/api/v1")
app.include_router(categories_routes.router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
