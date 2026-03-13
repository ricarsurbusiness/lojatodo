# Cart Service

Shopping cart microservice for the LojaTodo platform.

## Overview

The Cart Service handles:
- User shopping cart management
- Adding, updating, and removing items
- Integration with Product Service for validation
- Cart persistence using Redis

## Technology Stack

- **Framework**: FastAPI
- **Cache/Storage**: Redis
- **HTTP Client**: httpx (for product validation)

## Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|--------------|---------------|
| GET | `/api/v1/cart` | Get current user's cart | Yes |
| POST | `/api/v1/cart/add` | Add item to cart | Yes |
| POST | `/api/v1/cart/update` | Update item quantity | Yes |
| POST | `/api/v1/cart/remove?product_id={id}` | Remove item from cart | Yes |

## Request/Response Formats

### Add to Cart

**Request:**
```json
{
  "product_id": 1,
  "quantity": 2
}
```

### Update Cart Item

**Request:**
```json
{
  "product_id": 1,
  "quantity": 3
}
```

### Cart Response

```json
{
  "user_id": "user-123",
  "items": [
    {
      "product_id": 1,
      "quantity": 2,
      "price": 29.99,
      "name": "Product Name"
    }
  ],
  "total": 59.98
}
```

## Configuration

Environment variables (see `.env.example`):

| Variable | Description | Default |
|----------|-------------|---------|
| REDIS_HOST | Redis host | localhost |
| REDIS_PORT | Redis port | 6379 |
| PRODUCT_SERVICE_URL | Product service URL | http://localhost:8002 |
| AUTH_SERVICE_URL | Auth service URL | http://localhost:8001 |
| JWT_SECRET_KEY | JWT signing key | - |
| JWT_ALGORITHM | JWT algorithm | HS256 |

## Running Locally

### With Docker Compose

```bash
docker-compose up cart-service
```

### With Python

```bash
cd services/cart-service
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

## Testing

```bash
pytest -v
```

## Features

- **Automatic Product Validation**: When adding items, the cart service validates the product exists and retrieves the current price from the Product Service
- **Persistent Cart**: Cart data is stored in Redis and persists across sessions
- **Quantity Management**: Supports updating item quantities or removing items entirely
- **Price Calculation**: Cart total is calculated automatically based on product prices
