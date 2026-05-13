import structlog
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic_settings import BaseSettings

from webhook.routers.webhook import router
from webhook.services.sqs import SQSService


class Settings(BaseSettings):
    WHATSAPP_APP_SECRET: str
    WHATSAPP_VERIFY_TOKEN: str
    SQS_QUEUE_URL: str
    AWS_REGION: str = "us-east-1"
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"


def configure_logging(level: str) -> None:
    logging.basicConfig(level=getattr(logging, level))
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, level)),
        logger_factory=structlog.PrintLoggerFactory(),
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = Settings()
    configure_logging(settings.LOG_LEVEL)
    app.state.settings = settings
    app.state.sqs = SQSService(settings.SQS_QUEUE_URL, settings.AWS_REGION)
    yield


app = FastAPI(title="Boost Webhook", version="1.0.0", lifespan=lifespan)
app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "ok"}
