"""
Core configuration module for the Interface Agent application.
"""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "Interface Agent"
    app_version: str = "1.0.0"
    debug: bool = False

    # Database
    database_url: str
    database_pool_size: int = 20
    database_max_overflow: int = 10

    # Redis
    redis_url: str
    redis_max_connections: int = 50

    # RabbitMQ
    rabbitmq_url: str

    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # CORS
    allowed_origins: str = "http://localhost:3000"

    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    # ML Models
    ml_model_path: str = "/models"
    anomaly_threshold: float = 0.85

    # PII Detection
    pii_entities: str = "PERSON,EMAIL,PHONE_NUMBER,CREDIT_CARD,SSN,IP_ADDRESS"
    pii_redaction_char: str = "*"

    @property
    def pii_entities_list(self) -> List[str]:
        return [entity.strip() for entity in self.pii_entities.split(",")]

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # Monitoring
    prometheus_port: int = 9090
    enable_metrics: bool = True

    # Feature Flags
    enable_ml_anomaly: bool = True
    enable_pii_redaction: bool = True
    enable_plugin_system: bool = True
    enable_audit_log: bool = True

    # Celery
    celery_broker_url: str
    celery_result_backend: str

    # Autoscaling
    min_workers: int = 2
    max_workers: int = 10
    scale_up_threshold: int = 80
    scale_down_threshold: int = 20

    # Disaster Recovery
    backup_enabled: bool = True
    backup_schedule: str = "0 2 * * *"
    backup_retention_days: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
