from contextlib import asynccontextmanager
from datetime import datetime

import structlog
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api.routes import router as api_router
from app.core.exceptions.exceptions import LiaisonBaseException
from app.core.logging.logging import setup_logging
from app.core.telemetry.telemetry import setup_telemetry
from app.services.weaviate_service import weaviate_service

setup_logging()
logger = structlog.get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("application_startup", project_name=settings.PROJECT_NAME, version=settings.VERSION)
    yield
    
    logger.info("application_shutdown")
    try:
        weaviate_service.get_client().close()
        logger.info("weaviate_connection_closed")
    except Exception as e:
        logger.exception("weaviate_close_failed", error=str(e))

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenTelemetry
setup_telemetry(app)


# ---------------------------------------------------------
# Exception Handlers
# ---------------------------------------------------------
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Format Pydantic validation errors to be more frontend-friendly."""
    logger.error("validation_error", path=request.url.path, errors=str(exc.errors()))
    
    formatted_errors = []
    for error in exc.errors():
        loc = " -> ".join([str(loc_part) for loc_part in error["loc"] if loc_part != "body"])
        formatted_errors.append({"field": loc, "message": error["msg"]})

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation error", "errors": formatted_errors},
    )

@app.exception_handler(LiaisonBaseException)
async def liaison_exception_handler(request: Request, exc: LiaisonBaseException):
    """Handle custom application exceptions (like Rate Limits) gracefully."""
    logger.error("liaison_exception", path=request.url.path, status_code=exc.status_code, message=exc.message)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


# ---------------------------------------------------------
# Routes
# ---------------------------------------------------------
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/", tags=["Health"])
async def root(request: Request):
    """Root endpoint returning basic API information."""
    logger.info("root_endpoint_called")
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "healthy",
        "swagger_url": "/docs",
        "redoc_url": "/redoc",
    }

@app.get("/health", tags=["Health"])
async def health_check(request: Request):
    """Health check endpoint with Weaviate DB connectivity verification."""
    logger.info("health_check_called")

    # Ping the Vector DB to ensure the Docker container is alive
    client = weaviate_service.get_client()
    db_healthy = client.is_ready() if hasattr(client, "is_ready") else True

    response = {
        "status": "healthy" if db_healthy else "degraded",
        "version": settings.VERSION,
        "components": {
            "api": "healthy", 
            "weaviate_vector_db": "healthy" if db_healthy else "unhealthy"
        },
        "timestamp": datetime.now().isoformat(),
    }

    status_code = status.HTTP_200_OK if db_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(content=response, status_code=status_code)
