# Product Service

Product catalog management microservice for the LojaTodo platform.

## Overview

The Product Service handles:
- Product CRUD operations
- Category management
- Product search and filtering
- Pagination support

## Technology Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy (async)
- **Migrations**: Alembic
- **HTTP Client**: httpx (for service communication)

## Endpoints

### Products

| Method | Endpoint | Description | Auth Required |
|--------|----------|--------------|---------------|
| GET | `/api/v1/products` | List products (paginated) | No |
| GET | `/api/v1/products/{id}` | Get product by ID | No |
| POST | `/api/v1/products` | Create new product | Yes (admin) |
| PUT | `/api/v1/products/{id}` | Update product | Yes (admin) |
| DELETE | `/api/v1/products/{id}` | Delete product | Yes (admin) |

### Categories

| Method | Endpoint | Description | Auth Required |
|--------|----------|--------------|---------------|
| GET | `/api/v1/categories` | List categories | No |
| GET | `/api/v1/categories/{id}` | Get category by ID | No |
| POST | `/api/v1/categories` | Create new category | Yes (admin) |
| PUT | `/api/v1/categories/{id}` | Update category | Yes (admin) |
| DELETE | `/api/v1/categories/{id}` | Delete category | Yes (admin) |

## Query Parameters

### List Products

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| skip | int | 0 | Number of records to skip |
| limit | int | 20 | Maximum records to return (max 100) |
| search | str | None | Search term for product name |

## Configuration

Environment variables (see `.env.example`):

| Variable | Description | Default |
|----------|-------------|---------|
| POSTGRES_HOST | Database host | localhost |
| POSTGRES_PORT | Database port | 5432 |
| POSTGRES_USER | Database user | postgres |
| POSTGRES_PASSWORD | Database password | postgres |
| POSTGRES_DB | Database name | product_db |
| AUTH_SERVICE_URL | Auth service URL | http://localhost:8001 |
| JWT_SECRET_KEY | JWT signing key | - |
| JWT_ALGORITHM | JWT algorithm | HS256 |

## Running Locally

### With Docker Compose

```bash
docker-compose up product-service
```

### With Python

```bash
cd services/product-service
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

## Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Run migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1
```

## Testing

```bash
pytest -v
```

## Data Models

### Product

| Field | Type | Description |
|-------|------|-------------|
| id | int | Primary key |
| name | str | Product name |
| description | str | Product description |
| price | float | Product price |
| category_id | int | Foreign key to category |
| stock | int | Stock quantity |
| created_at | datetime | Creation timestamp |
| updated_at | datetime | Last update timestamp |

### Category

| Field | Type | Description |
|-------|------|-------------|
| id | int | Primary key |
| name | str | Category name |
| description | str | Category description |
| parent_id | int | Parent category (nullable) |
