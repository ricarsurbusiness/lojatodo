# Analytics Service

Analytics and metrics microservice for the e-commerce platform.

## Endpoints

- `GET /api/v1/analytics/sales` - Sales metrics (total revenue, today/week/month revenue)
- `GET /api/v1/analytics/orders` - Order analytics (orders by status, trends)
- `GET /api/v1/analytics/products` - Product performance (top products, units sold)
- `GET /api/v1/analytics/users` - User analytics (registrations, active users)

## Configuration

Environment variables:
- `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
- `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB`
- `RABBITMQ_HOST`, `RABBITMQ_PORT`, `RABBITMQ_USER`, `RABBITMQ_PASSWORD`
- `AUTH_SERVICE_URL`
- `JWT_SECRET_KEY`, `JWT_ALGORITHM`
- `CACHE_TTL` (default: 300 seconds)

## Running

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8004
```

## Docker

```bash
docker build -t analytics-service .
docker run -p 8004:8004 analytics-service
```
