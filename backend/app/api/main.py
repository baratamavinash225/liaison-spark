from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

import structlog
from app.core.logging.logging import setup_logging
from app.core.telemetry.telemetry import setup_telemetry

load_dotenv()
from app.api.routes import router as api_router

setup_logging()
logger = structlog.get_logger(__name__)

app = FastAPI(title="Liaison-Spark API")

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

@app.on_event("startup")
async def startup_event():
    logger.info("application_started", framework="FastAPI", env="development")
