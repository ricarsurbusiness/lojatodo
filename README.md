# LojaTodo - Ecommerce Microservices Platform

A scalable full-stack Ecommerce platform built with Python microservices architecture. The system is designed to be modular, scalable, and production-ready using modern backend and DevOps practices.

## Architecture

```
                           Internet
                              |
                         CDN / WAF
                              |
                         Load Balancer
                              |
                         API Gateway
                              |
     ---------------------------------------------------------
     |          |           |          |           |          |
   Auth     Product       Cart      Order     Payment    Inventory
    Svc       Svc         Svc        Svc         Svc        Svc
     |          |           |          |           |          |
    DB         DB        Redis       DB          DB          DB
                              |
                          Message Broker
                          (Kafka/RabbitMQ)
```

## Tech Stack

- **Backend**: Python, FastAPI, SQLAlchemy, Alembic
- **Databases**: PostgreSQL (Auth, Product, Order, Payment, Inventory), Redis (Cart, Cache)
- **Container**: Docker, Docker Compose
- **Authentication**: JWT, bcrypt

## Services

| Service | Port | Description |
|---------|------|-------------|
| auth-service | 8001 | Authentication & user management |
| product-service | 8002 | Product catalog & categories |
| cart-service | 8003 | Shopping cart management |
| order-service | 8004 | Order creation, listing, details and cancellation |
| inventory-service | 8005 | Stock reservation, confirmation and release |
| payment-service | 8006 | Multi-provider payment processing |
| notification-service | 8007 | Email notifications and messaging |
| analytics-service | 8008 | Analytics, reporting and data aggregation |
| admin-service | 8009 | Admin dashboard, RBAC, audit logs |

## Quick Start

### Prerequisites

- Docker
- Docker Compose
- Make (optional, for convenience commands)

### Running Services

```bash
# Start all services
make up

# Or using docker-compose directly
docker-compose up -d
```

Services will be available at:
- Auth Service: http://localhost:8001
- Product Service: http://localhost:8002
- Cart Service: http://localhost:8003
- Order Service: http://localhost:8004
- Inventory Service: http://localhost:8005
- Payment Service: http://localhost:8006
- Notification Service: http://localhost:8007
- Analytics Service: http://localhost:8008
- Admin Service: http://localhost:8009
- RabbitMQ Management: http://localhost:15672

### Stopping Services

```bash
make down
```

## API Endpoints

### Auth Service (Port 8001)

| Method | Endpoint | Description | Auth Required |
|--------|----------|--------------|---------------|
| POST | `/api/v1/auth/register` | Register new user | No |
| POST | `/api/v1/auth/login` | Login | No |
| POST | `/api/v1/auth/refresh` | Refresh token | No |
| GET | `/api/v1/me` | Get current user | Yes |
| PUT | `/api/v1/profile` | Update profile | Yes |
| POST | `/api/v1/assign-role` | Assign role to user | Yes (admin) |

### Product Service (Port 8002)

| Method | Endpoint | Description | Auth Required |
|--------|----------|--------------|---------------|
| GET | `/api/v1/products` | List products | No |
| GET | `/api/v1/products/{id}` | Get product | No |
| POST | `/api/v1/products` | Create product | Yes (admin) |
| PUT | `/api/v1/products/{id}` | Update product | Yes (admin) |
| DELETE | `/api/v1/products/{id}` | Delete product | Yes (admin) |
| GET | `/api/v1/categories` | List categories | No |
| GET | `/api/v1/categories/{id}` | Get category | No |
| POST | `/api/v1/categories` | Create category | Yes (admin) |
| PUT | `/api/v1/categories/{id}` | Update category | Yes (admin) |
| DELETE | `/api/v1/categories/{id}` | Delete category | Yes (admin) |

### Cart Service (Port 8003)

| Method | Endpoint | Description | Auth Required |
|--------|----------|--------------|---------------|
| GET | `/api/v1/cart` | Get cart | Yes |
| POST | `/api/v1/cart/add` | Add item to cart | Yes |
| POST | `/api/v1/cart/update` | Update item quantity | Yes |
| POST | `/api/v1/cart/remove` | Remove item from cart | Yes |

### Order Service (Port 8004)

| Method | Endpoint | Description | Auth Required |
|--------|----------|--------------|---------------|
| POST | `/api/v1/orders` | Create order | Yes |
| GET | `/api/v1/orders` | List user orders | Yes |
| GET | `/api/v1/orders/{id}` | Get order details | Yes |
| PUT | `/api/v1/orders/{id}/cancel` | Cancel order | Yes |

### Inventory Service (Port 8005)

| Method | Endpoint | Description | Auth Required |
|--------|----------|--------------|---------------|
| GET | `/api/v1/inventory/{product_id}` | Get stock details | No |
| POST | `/api/v1/inventory` | Create inventory record | Yes |
| POST | `/api/v1/inventory/reserve` | Reserve stock | Yes |
| POST | `/api/v1/inventory/confirm` | Confirm reservation | Yes |
| POST | `/api/v1/inventory/release` | Release reservation | Yes |

### Payment Service (Port 8006)

| Method | Endpoint | Description | Auth Required |
|--------|----------|--------------|---------------|
| POST | `/api/v1/payments/charge` | Charge payment with provider | Yes |
| GET | `/api/v1/payments/{id}` | Get payment details | Yes |
| POST | `/api/v1/payments/webhook` | Provider webhook receiver | No |

## Roles & Permissions

| Role | Description |
|------|-------------|
| superAdmin | Full system control |
| admin | Store, product, inventory, orders, payments, analytics |
| cliente | Orders, payments only |

## Development Setup

### Running Tests

```bash
# Run all tests
make test

# Run specific service tests
make test-auth
make test-product
make test-cart
make test-order
make test-inventory
make test-payment
make test-notification
make test-analytics
make test-admin
```

### Running Linters

```bash
# Run all linters
make lint

# Run specific service linter
make lint-auth
make lint-product
make lint-cart
make lint-order
make lint-inventory
make lint-payment
make lint-notification
make lint-analytics
make lint-admin
```

### Running Migrations

```bash
# Run all migrations
make migrate

# Run specific service migrations
make migrate-auth
make migrate-product
```

### Building Images

```bash
# Build all service images
make build

# Build specific service image
make build-auth
make build-product
make build-cart
make build-order
make build-inventory
make build-payment
make build-notification
make build-analytics
make build-admin
```

### Viewing Logs

```bash
make logs
```

### Clean Up

```bash
# Stop services and remove volumes
make clean
```

## Environment Variables

Copy the example environment files and configure as needed:

```bash
cp services/auth-service/.env.example services/auth-service/.env
cp services/product-service/.env.example services/product-service/.env
cp services/cart-service/.env.example services/cart-service/.env
cp services/order-service/.env.example services/order-service/.env
cp services/inventory-service/.env.example services/inventory-service/.env
cp services/payment-service/.env.example services/payment-service/.env
cp services/notification-service/.env.example services/notification-service/.env
cp services/analytics-service/.env.example services/analytics-service/.env
cp services/admin-service/.env.example services/admin-service/.env
```

## Project Structure

```
ecommerce-microservices/
├── docker-compose.yml
├── Makefile
├── README.md
├── services/
│   ├── auth-service/
│   │   ├── app/
│   │   │   ├── api/
│   │   │   ├── core/
│   │   │   ├── db/
│   │   │   ├── models/
│   │   │   ├── repositories/
│   │   │   ├── schemas/
│   │   │   ├── services/
│   │   │   └── main.py
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── pytest.ini
│   ├── product-service/
│   │   ├── app/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── pytest.ini
│   └── cart-service/
│       ├── app/
│       ├── Dockerfile
│       ├── requirements.txt
│       └── pytest.ini
│   ├── order-service/
│   │   ├── app/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── pytest.ini
│   ├── inventory-service/
│   │   ├── app/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── pytest.ini
│   └── payment-service/
│       ├── app/
│       ├── Dockerfile
│       ├── requirements.txt
│       └── pytest.ini
└── shared/
    ├── libraries/
    ├── schemas/
    └── utils/
```

## License

MIT
