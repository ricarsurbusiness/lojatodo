# Auth Service

Authentication and authorization microservice for the LojaTodo platform.

## Overview

The Auth Service handles:
- User registration and authentication
- JWT token generation and validation
- Role-based access control (RBAC)
- User profile management

## Technology Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **Authentication**: JWT (python-jose), bcrypt
- **ORM**: SQLAlchemy (async)
- **Migrations**: Alembic

## Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|--------------|---------------|
| POST | `/api/v1/auth/register` | Register a new user | No |
| POST | `/api/v1/auth/login` | Login and get tokens | No |
| POST | `/api/v1/auth/refresh` | Refresh access token | No |

### User Management

| Method | Endpoint | Description | Auth Required |
|--------|----------|--------------|---------------|
| GET | `/api/v1/me` | Get current user profile | Yes |
| PUT | `/api/v1/profile` | Update user profile | Yes |
| POST | `/api/v1/assign-role` | Assign role to user | Yes (admin) |

## Configuration

Environment variables (see `.env.example`):

| Variable | Description | Default |
|----------|-------------|---------|
| POSTGRES_HOST | Database host | localhost |
| POSTGRES_PORT | Database port | 5432 |
| POSTGRES_USER | Database user | postgres |
| POSTGRES_PASSWORD | Database password | postgres |
| POSTGRES_DB | Database name | auth_db |
| JWT_SECRET_KEY | JWT signing key | - |
| JWT_ALGORITHM | JWT algorithm | HS256 |
| ACCESS_TOKEN_EXPIRE_MINUTES | Access token expiry | 30 |
| REFRESH_TOKEN_EXPIRE_DAYS | Refresh token expiry | 7 |

## Running Locally

### With Docker Compose

```bash
docker-compose up auth-service
```

### With Python

```bash
cd services/auth-service
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

## Roles

| Role | Description |
|------|-------------|
| superAdmin | Full system control |
| admin | Store management |
| cliente | End user |
