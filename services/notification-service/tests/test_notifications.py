import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def mock_celery():
    with patch("app.api.v1.routes.notifications_routes.send_email_task") as mock:
        mock.delay = MagicMock()
        yield mock


@pytest.mark.asyncio
async def test_health_check():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


@pytest.mark.asyncio
async def test_send_notification(mock_celery):
    with patch("app.api.v1.routes.notifications_routes.get_notification_db") as mock_get_db:
        mock_session = AsyncMock()
        mock_get_db.return_value = iter([mock_session])

        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_session.execute = AsyncMock(return_value=mock_result)

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/notifications/send",
                json={
                    "email": "test@example.com",
                    "subject": "Test Subject",
                    "body": "Test Body",
                },
            )

        assert response.status_code == 201
        data = response.json()
        assert "notification_id" in data
        assert data["status"] == "pending"
        mock_celery.delay.assert_called_once()


@pytest.mark.asyncio
async def test_send_notification_duplicate_correlation_id():
    with patch("app.api.v1.routes.notifications_routes.get_notification_db") as mock_get_db:
        mock_session = AsyncMock()
        mock_get_db.return_value = iter([mock_session])

        mock_existing_notification = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_existing_notification)
        mock_session.execute = AsyncMock(return_value=mock_result)

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/notifications/send",
                json={
                    "email": "test@example.com",
                    "subject": "Test Subject",
                    "body": "Test Body",
                    "correlation_id": "duplicate-key",
                },
            )

        assert response.status_code == 409


@pytest.mark.asyncio
async def test_get_notification_not_found():
    with patch("app.api.v1.routes.notifications_routes.get_notification_db") as mock_get_db:
        mock_session = AsyncMock()
        mock_get_db.return_value = iter([mock_session])

        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_session.execute = AsyncMock(return_value=mock_result)

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/notifications/999")

        assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_notification_found():
    with patch("app.api.v1.routes.notifications_routes.get_notification_db") as mock_get_db:
        mock_session = AsyncMock()
        mock_get_db.return_value = iter([mock_session])

        mock_notification = MagicMock()
        mock_notification.id = 1
        mock_notification.email = "test@example.com"
        mock_notification.subject = "Test"
        mock_notification.body = "Body"
        mock_notification.status = "pending"
        mock_notification.correlation_id = None
        mock_notification.sendgrid_message_id = None
        mock_notification.failure_reason = None
        mock_notification.created_at = "2024-01-01T00:00:00"
        mock_notification.sent_at = None

        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=mock_notification)
        mock_session.execute = AsyncMock(return_value=mock_result)

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/notifications/1")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["email"] == "test@example.com"


def test_email_service_initialization():
    with patch("app.services.email_service.SendGridAPIClient"):
        from app.services.email_service import EmailService
        service = EmailService()
        assert service is not None
