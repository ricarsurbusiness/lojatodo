from pydantic_settings import BaseSettings


class AdminServiceSettings(BaseSettings):
    AUTH_SERVICE_URL: str = "http://localhost:8001"
    ORDER_SERVICE_URL: str = "http://localhost:8002"
    PRODUCT_SERVICE_URL: str = "http://localhost:8003"
    PAYMENT_SERVICE_URL: str = "http://localhost:8004"
    ANALYTICS_SERVICE_URL: str = "http://localhost:8005"
    
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


admin_settings = AdminServiceSettings()
