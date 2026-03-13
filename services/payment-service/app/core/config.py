from pydantic_settings import BaseSettings


class PaymentServiceSettings(BaseSettings):
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "payment_db"

    AUTH_SERVICE_URL: str = "http://localhost:8001"

    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"

    STRIPE_API_KEY: str = "stripe_test_key"
    PAYPAL_CLIENT_ID: str = "paypal_test_client_id"
    PAYPAL_CLIENT_SECRET: str = "paypal_test_secret"
    MERCADOPAGO_ACCESS_TOKEN: str = "mp_test_token"

    IDEMPOTENCY_TTL_HOURS: int = 24

    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASSWORD: str = "guest"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def RABBITMQ_URL(self) -> str:
        return (
            f"amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASSWORD}"
            f"@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}//"
        )

    class Config:
        env_file = ".env"
        case_sensitive = True


payment_settings = PaymentServiceSettings()
