from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

import structlog
from app.core.logging.logging import setup_logging
from app.core.telemetry.telemetry import setup_telemetry

load_dotenv()
from app.api.routes import router as api_router

setup_logging()
logger = structlog.get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("application_started", framework="FastAPI", env="development")
    yield

app = FastAPI(title="Liaison-Spark API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenTelemetry
setup_telemetry(app)

app.include_router(api_router, prefix="/api")
