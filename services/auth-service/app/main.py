from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.session import engine, Base
from app.api.v1.routes import auth_routes, users_routes
from app.models.user_model import User
from app.models.role_model import Role


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    await seed_roles()
    
    yield
    
    await engine.dispose()


async def seed_roles():
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy import select
    from app.db.session import AsyncSessionLocal
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Role))
        existing_roles = result.scalars().all()
        
        if len(existing_roles) < 3:
            roles_to_create = []
            if not any(r.name == "superAdmin" for r in existing_roles):
                roles_to_create.append(Role(name="superAdmin", description="Full system control"))
            if not any(r.name == "admin" for r in existing_roles):
                roles_to_create.append(Role(name="admin", description="Store, product, inventory, orders, payments, analytics"))
            if not any(r.name == "cliente" for r in existing_roles):
                roles_to_create.append(Role(name="cliente", description="Orders, payments only"))
            
            for role in roles_to_create:
                session.add(role)
            
            await session.commit()


app = FastAPI(
    title="Auth Service",
    description="Authentication and authorization microservice",
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

app.include_router(auth_routes.router, prefix="/api/v1")
app.include_router(users_routes.router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
