# Notification Service

Microservice for handling email notifications and event-driven messaging.

## Features

- Send email notifications via SendGrid API
- Asynchronous email processing with Celery
- RabbitMQ event consumer for order and payment events
- REST API for notification management

## API Endpoints

### POST /api/v1/notifications/send
Send a notification email.

**Request:**
```json
{
  "email": "user@example.com",
  "subject": "Notification Subject",
  "body": "<html>Body content</html>",
  "correlation_id": "optional-correlation-id"
}
```

**Response:**
```json
{
  "notification_id": 1,
  "status": "pending"
}
```

### GET /api/v1/notifications/{id}
Get notification status by ID.

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "subject": "Notification Subject",
  "body": "<html>Body content</html>",
  "status": "sent",
  "correlation_id": "optional-correlation-id",
  "sendgrid_message_id": "abc123",
  "failure_reason": null,
  "created_at": "2024-01-01T00:00:00",
  "sent_at": "2024-01-01T00:01:00"
}
```

### GET /health
Health check endpoint.

## Event Handling

The service consumes the following events from RabbitMQ:

- `ORDER_CREATED` - Order confirmation emails
- `PAYMENT_COMPLETED` - Payment confirmation emails
- `PAYMENT_FAILED` - Payment failure notification
- `ORDER_SHIPPED` - Shipping notification

## Running the Service

### With Docker
```bash
docker build -t notification-service .
docker run -p 8007:8007 notification-service
```

### Local Development
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8007
```

### Running Celery Worker
```bash
celery -A celery_app worker --loglevel=info
```

## Environment Variables

- `POSTGRES_HOST` - PostgreSQL host (default: localhost)
- `POSTGRES_PORT` - PostgreSQL port (default: 5432)
- `POSTGRES_USER` - PostgreSQL user (default: postgres)
- `POSTGRES_PASSWORD` - PostgreSQL password (default: postgres)
- `POSTGRES_DB` - Database name (default: notification_db)
- `RABBITMQ_HOST` - RabbitMQ host (default: localhost)
- `RABBITMQ_PORT` - RabbitMQ port (default: 5672)
- `RABBITMQ_USER` - RabbitMQ user (default: guest)
- `RABBITMQ_PASSWORD` - RabbitMQ password (default: guest)
- `SENDGRID_API_KEY` - SendGrid API key
- `SENDGRID_FROM_EMAIL` - Sender email (default: noreply@lojatodo.com)
- `SENDGRID_FROM_NAME` - Sender name (default: LojaTodo)
