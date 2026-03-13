# Payment Service

Payment processing microservice for the LojaTodo platform.

## Overview

The Payment Service handles:
- Payment processing with multiple providers (Stripe, PayPal, MercadoPago)
- Unified payment interface using Abstract Factory pattern
- Idempotency support for duplicate request prevention
- Webhook handling for asynchronous payment status updates

## Technology Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **Payment Providers**: Stripe, PayPal, MercadoPago
- **ORM**: SQLAlchemy (async)
- **Migrations**: Alembic

## Endpoints

### Payments

| Method | Endpoint | Description | Auth Required |
|--------|----------|--------------|---------------|
| POST | `/api/v1/payments/charge` | Process a payment | Yes |
| GET | `/api/v1/payments/{id}` | Get payment status | Yes |
| POST | `/api/v1/payments/webhook` | Provider webhook callback | No |

## Payment Flow

```
1. Client sends POST /payments/charge with:
   - order_id: The order to charge
   - amount: Payment amount
   - currency: Currency code (default: USD)
   - provider: Payment provider (stripe, paypal, mercadopago)
   - payment_method: Provider-specific payment details
   - idempotency_key: Unique key to prevent duplicate charges

2. Service validates idempotency key (24-hour TTL)

3. Payment provider processes the charge

4. Response includes:
   - payment id
   - status (succeeded, failed)
   - provider_transaction_id
```

## Configuration

Environment variables (see `.env.example`):

| Variable | Description | Default |
|----------|-------------|---------|
| POSTGRES_HOST | Database host | localhost |
| POSTGRES_PORT | Database port | 5432 |
| POSTGRES_USER | Database user | postgres |
| POSTGRES_PASSWORD | Database password | postgres |
| POSTGRES_DB | Database name | payment_db |
| AUTH_SERVICE_URL | Auth service URL | http://localhost:8001 |
| JWT_SECRET_KEY | JWT signing key | - |
| JWT_ALGORITHM | JWT algorithm | HS256 |
| STRIPE_API_KEY | Stripe API key | - |
| PAYPAL_CLIENT_ID | PayPal client ID | - |
| PAYPAL_CLIENT_SECRET | PayPal client secret | - |
| MERCADOPAGO_ACCESS_TOKEN | MercadoPago access token | - |
| IDEMPOTENCY_TTL_HOURS | Idempotency key TTL | 24 |

## Payment Providers

### Stripe
- Requires `card_token` in payment_method
- Returns Stripe transaction ID on success

### PayPal
- Requires `paypal_order_id` in payment_method
- Returns PayPal transaction ID on success

### MercadoPago
- Requires `mp_token` in payment_method
- Returns MercadoPago transaction ID on success

## Running Locally

### With Docker Compose

```bash
docker-compose up payment-service
```

### With Python

```bash
cd services/payment-service
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

## Testing

```bash
pytest -v
```

## Payment Status Lifecycle

```
pending → processing → succeeded
                    → failed
```

- **pending**: Initial state when payment is created
- **processing**: Payment is being processed by provider
- **succeeded**: Payment completed successfully
- **failed**: Payment failed (insufficient funds, invalid method, etc.)
