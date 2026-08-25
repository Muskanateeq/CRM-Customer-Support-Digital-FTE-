"""
Custora Customer Success FTE - Main FastAPI Application
Production-ready API with all middleware, error handling, and monitoring
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from datetime import datetime
from contextlib import asynccontextmanager
import time
import logging

from src.config import settings
from src.database.client import init_db_pool, close_db_pool, check_db_health
from src.utils.logging import setup_logging, set_correlation_id, get_correlation_id

# Setup logging
setup_logging(log_level=settings.LOG_LEVEL, environment=settings.ENVIRONMENT)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.

    This replaces the deprecated @app.on_event decorators.
    """
    # ============================================
    # STARTUP
    # ============================================
    logger.info("=" * 70)
    logger.info("Custora Customer Success FTE - Starting Up")
    logger.info("=" * 70)
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"API Host: {settings.API_HOST}:{settings.API_PORT}")
    logger.info(f"Database: {settings.POSTGRES_HOST}/{settings.POSTGRES_DB}")
    logger.info(f"OpenAI Model: {settings.AGENT_MODEL}")
    logger.info("Channels Enabled:")
    logger.info(f"  - Email (Gmail): {settings.GMAIL_ENABLED}")
    logger.info(f"  - WhatsApp (Twilio): {settings.WHATSAPP_ENABLED}")
    logger.info(f"  - Web Form: {settings.WEBFORM_ENABLED}")
    logger.info("=" * 70)

    try:
        # Initialize database connection pool
        await init_db_pool()
        logger.info("[OK] Database pool initialized")

        # Initialize channel handlers
        from src.channels.email_handler import get_gmail_handler
        from src.channels.whatsapp_handler import get_whatsapp_handler
        from src.channels.webform_handler import get_webform_handler

        # Initialize handlers (they will check if enabled)
        get_gmail_handler()
        get_whatsapp_handler()
        get_webform_handler()
        logger.info("[OK] Channel handlers initialized")

        # Initialize Kafka producer
        if settings.KAFKA_ENABLED:
            from src.kafka.producer import get_kafka_producer
            await get_kafka_producer()
            logger.info("[OK] Kafka producer initialized")
        else:
            logger.info("[WARN]  Kafka disabled in settings")

        from src.services.channel_jobs import start_channel_job_worker
        await start_channel_job_worker()
        logger.info("[OK] Durable channel job worker initialized")

        logger.info("=" * 70)
        logger.info("[OK] Startup complete - Ready to serve requests")
        logger.info("=" * 70)

    except Exception as e:
        logger.error(f"[FAIL] Startup failed: {e}", exc_info=True)
        raise

    yield  # Application runs here

    # ============================================
    # SHUTDOWN
    # ============================================
    logger.info("=" * 70)
    logger.info("Custora Customer Success FTE - Shutting Down")
    logger.info("=" * 70)

    try:
        from src.services.channel_jobs import stop_channel_job_worker
        await stop_channel_job_worker()
        logger.info("[OK] Durable channel job worker stopped")

        # Close database pool
        await close_db_pool()
        logger.info("[OK] Database pool closed")

        # Close Kafka producer
        if settings.KAFKA_ENABLED:
            from src.kafka.producer import _producer_instance
            if _producer_instance:
                await _producer_instance.stop()
                logger.info("[OK] Kafka producer closed")

        # Channel handlers don't need explicit cleanup

        logger.info("=" * 70)
        logger.info("[OK] Shutdown complete")
        logger.info("=" * 70)

    except Exception as e:
        logger.error(f"Error during shutdown: {e}", exc_info=True)


# Create FastAPI application
app = FastAPI(
    title="Custora Customer Success FTE API",
    description="24/7 AI-powered customer support across Email, WhatsApp, and Web Form",
    version="2.0.0",
    docs_url="/docs" if settings.ENABLE_DOCS else None,
    redoc_url="/redoc" if settings.ENABLE_DOCS else None,
    lifespan=lifespan
)


# ============================================
# Middleware
# ============================================

@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    """
    Middleware to add correlation ID to all requests.

    Correlation IDs help track requests across services and logs.
    """
    # Get or create correlation ID
    correlation_id = request.headers.get('X-Correlation-ID')
    if not correlation_id:
        correlation_id = set_correlation_id()
    else:
        set_correlation_id(correlation_id)

    # Process request
    response = await call_next(request)

    # Add correlation ID to response headers
    response.headers['X-Correlation-ID'] = correlation_id

    return response


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    """
    Middleware to log all requests with timing information.
    """
    start_time = time.time()

    # Log request
    logger.info(
        f"Request started: {request.method} {request.url.path}",
        extra={
            'method': request.method,
            'path': request.url.path,
            'client_ip': request.client.host if request.client else 'unknown'
        }
    )

    # Process request
    response = await call_next(request)

    # Calculate duration
    duration_ms = (time.time() - start_time) * 1000

    # Log response
    logger.info(
        f"Request completed: {request.method} {request.url.path} - "
        f"Status: {response.status_code} - Duration: {duration_ms:.2f}ms",
        extra={
            'method': request.method,
            'path': request.url.path,
            'status_code': response.status_code,
            'duration_ms': duration_ms
        }
    )

    # Add timing header
    response.headers['X-Response-Time'] = f"{duration_ms:.2f}ms"

    return response


# CORS middleware for web form
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "https://custora-tau.vercel.app",
        "https://dzon-developer-custora-backend.hf.space"
    ] if not settings.is_development else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# Exception Handlers
# ============================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors."""
    logger.warning(
        f"Validation error: {exc.errors()}",
        extra={'path': request.url.path, 'errors': exc.errors()}
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation error",
            "detail": exc.errors(),
            "correlation_id": get_correlation_id()
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions."""
    logger.error(
        f"Unhandled exception: {exc}",
        exc_info=True,
        extra={'path': request.url.path}
    )

    # Don't expose internal errors in production
    error_detail = str(exc) if settings.is_development else "An internal error occurred"

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": error_detail,
            "correlation_id": get_correlation_id()
        }
    )


"""
Custora Customer Success FTE - Main FastAPI Application
Production-ready API with all middleware, error handling, and monitoring.
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.config import settings
from src.database.client import (
    init_db_pool,
    close_db_pool,
    check_db_health,
)
from src.database.migrations import ensure_channel_jobs_schema
from src.utils.logging import (
    setup_logging,
    set_correlation_id,
    get_correlation_id,
)


# ============================================
# Logging Configuration
# ============================================

setup_logging(
    log_level=settings.LOG_LEVEL,
    environment=settings.ENVIRONMENT,
)

logger = logging.getLogger(__name__)


# ============================================
# Gmail Background Polling
# ============================================

async def run_email_polling_loop():
    """
    Run the existing Gmail polling function every 30 seconds.

    poll_emails() uses synchronous requests, therefore it is
    executed in a background thread to avoid blocking FastAPI.
    """

    from scripts.poll_emails import poll_emails

    logger.info("[OK] Gmail polling background task started")

    # Lifespan tasks are scheduled just before uvicorn begins accepting HTTP
    # requests. Give the local server a moment to bind before the first poll.
    await asyncio.sleep(1)

    while True:
        try:
            # Run synchronous polling function in a background thread.
            await asyncio.to_thread(poll_emails)

            # Wait 30 seconds before checking Gmail again.
            await asyncio.sleep(30)

        except asyncio.CancelledError:
            logger.info("[OK] Gmail polling background task cancelled")
            raise

        except Exception as exc:
            logger.error(
                f"Gmail polling background task failed: {exc}",
                exc_info=True,
            )

            # Retry after 30 seconds if an unexpected error occurs.
            await asyncio.sleep(30)


# ============================================
# FastAPI Lifespan
# ============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """

    email_polling_task = None

    # ============================================
    # STARTUP
    # ============================================

    logger.info("=" * 70)
    logger.info("Custora Customer Success FTE - Starting Up")
    logger.info("=" * 70)
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"API Host: {settings.API_HOST}:{settings.API_PORT}")
    logger.info(
        f"Database: {settings.POSTGRES_HOST}/{settings.POSTGRES_DB}"
    )
    logger.info(f"OpenAI Model: {settings.AGENT_MODEL}")
    logger.info("Channels Enabled:")
    logger.info(f"  - Email (Gmail): {settings.GMAIL_ENABLED}")
    logger.info(f"  - WhatsApp (Twilio): {settings.WHATSAPP_ENABLED}")
    logger.info(f"  - Web Form: {settings.WEBFORM_ENABLED}")
    logger.info("=" * 70)

    try:
        # Initialize database connection pool.
        await init_db_pool()
        logger.info("[OK] Database pool initialized")

        # The durable worker must never start before its queue table exists.
        # Run this idempotent migration here as a fallback for Render services
        # where a pre-deploy command is unavailable or not configured.
        await ensure_channel_jobs_schema()

        # Import channel handlers.
        from src.channels.email_handler import get_gmail_handler
        from src.channels.whatsapp_handler import get_whatsapp_handler
        from src.channels.webform_handler import get_webform_handler

        # Initialize channel handlers.
        get_gmail_handler()
        get_whatsapp_handler()
        get_webform_handler()

        logger.info("[OK] Channel handlers initialized")

        # Start Gmail polling task inside the Render web service.
        if settings.GMAIL_ENABLED:
            email_polling_task = asyncio.create_task(
                run_email_polling_loop(),
                name="gmail-email-poller",
            )

            logger.info("[OK] Gmail polling task scheduled")

        else:
            logger.warning(
                "[WARN] Gmail polling not started because Gmail is disabled"
            )

        # Initialize Kafka producer if enabled.
        if settings.KAFKA_ENABLED:
            from src.kafka.producer import get_kafka_producer

            await get_kafka_producer()
            logger.info("[OK] Kafka producer initialized")

        else:
            logger.warning("[WARN] Kafka disabled in settings")

        # Start durable channel job worker.
        from src.services.channel_jobs import start_channel_job_worker

        await start_channel_job_worker()
        logger.info("[OK] Durable channel job worker initialized")

        logger.info("=" * 70)
        logger.info("[OK] Startup complete - Ready to serve requests")
        logger.info("=" * 70)

    except Exception as exc:
        logger.error(
            f"[FAIL] Startup failed: {exc}",
            exc_info=True,
        )
        raise

    # Application runs here.
    yield

    # ============================================
    # SHUTDOWN
    # ============================================

    logger.info("=" * 70)
    logger.info("Custora Customer Success FTE - Shutting Down")
    logger.info("=" * 70)

    try:
        # Stop Gmail polling task.
        if email_polling_task:
            email_polling_task.cancel()

            try:
                await email_polling_task
            except asyncio.CancelledError:
                pass

            logger.info("[OK] Gmail polling task stopped")

        # Stop channel job worker.
        from src.services.channel_jobs import stop_channel_job_worker

        await stop_channel_job_worker()
        logger.info("[OK] Durable channel job worker stopped")

        # Close database pool.
        await close_db_pool()
        logger.info("[OK] Database pool closed")

        # Close Kafka producer if enabled.
        if settings.KAFKA_ENABLED:
            from src.kafka.producer import _producer_instance

            if _producer_instance:
                await _producer_instance.stop()
                logger.info("[OK] Kafka producer closed")

        logger.info("=" * 70)
        logger.info("[OK] Shutdown complete")
        logger.info("=" * 70)

    except Exception as exc:
        logger.error(
            f"Error during shutdown: {exc}",
            exc_info=True,
        )


# ============================================
# Create FastAPI Application
# ============================================

app = FastAPI(
    title="Custora Customer Success FTE API",
    description=(
        "24/7 AI-powered customer support across "
        "Email, WhatsApp, and Web Form"
    ),
    version="2.0.0",
    docs_url="/docs" if settings.ENABLE_DOCS else None,
    redoc_url="/redoc" if settings.ENABLE_DOCS else None,
    lifespan=lifespan,
)


# ============================================
# Middleware
# ============================================

@app.middleware("http")
async def correlation_id_middleware(
    request: Request,
    call_next,
):
    """
    Add a correlation ID to every request.
    """

    correlation_id = request.headers.get("X-Correlation-ID")

    if not correlation_id:
        correlation_id = set_correlation_id()
    else:
        set_correlation_id(correlation_id)

    response = await call_next(request)

    response.headers["X-Correlation-ID"] = correlation_id

    return response


@app.middleware("http")
async def request_logging_middleware(
    request: Request,
    call_next,
):
    """
    Log all incoming HTTP requests.
    """

    start_time = time.time()

    logger.info(
        f"Request started: {request.method} {request.url.path}",
        extra={
            "method": request.method,
            "path": request.url.path,
            "client_ip": (
                request.client.host
                if request.client
                else "unknown"
            ),
        },
    )

    response = await call_next(request)

    duration_ms = (time.time() - start_time) * 1000

    logger.info(
        f"Request completed: {request.method} "
        f"{request.url.path} - "
        f"Status: {response.status_code} - "
        f"Duration: {duration_ms:.2f}ms",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
        },
    )

    response.headers["X-Response-Time"] = (
        f"{duration_ms:.2f}ms"
    )

    return response


# ============================================
# CORS Middleware
# ============================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=(
        [
            "http://localhost:3000",
            "http://localhost:3001",
            "https://custora-tau.vercel.app",
            "https://dzon-developer-custora-backend.hf.space",
        ]
        if not settings.is_development
        else ["*"]
    ),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# Exception Handlers
# ============================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    """
    Handle Pydantic validation errors.
    """

    logger.warning(
        f"Validation error: {exc.errors()}",
        extra={
            "path": request.url.path,
            "errors": exc.errors(),
        },
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation error",
            "detail": exc.errors(),
            "correlation_id": get_correlation_id(),
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception,
):
    """
    Handle all unhandled exceptions.
    """

    logger.error(
        f"Unhandled exception: {exc}",
        exc_info=True,
        extra={"path": request.url.path},
    )

    error_detail = (
        str(exc)
        if settings.is_development
        else "An internal error occurred"
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": error_detail,
            "correlation_id": get_correlation_id(),
        },
    )


# ============================================
# Core Endpoints
# ============================================

@app.api_route("/", methods=["GET", "HEAD"])
async def root():
    """
    Root endpoint with service information.
    """

    return {
        "service": "Custora Customer Success FTE",
        "version": "2.0.0",
        "status": "operational",
        "environment": settings.ENVIRONMENT,
        "channels": {
            "email": settings.GMAIL_ENABLED,
            "whatsapp": settings.WHATSAPP_ENABLED,
            "web_form": settings.WEBFORM_ENABLED,
        },
        "documentation": (
            "/docs"
            if not settings.is_production
            else None
        ),
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """

    db_healthy = await check_db_health()

    is_healthy = db_healthy

    status_code = (
        status.HTTP_200_OK
        if is_healthy
        else status.HTTP_503_SERVICE_UNAVAILABLE
    )

    return JSONResponse(
        status_code=status_code,
        content={
            "status": (
                "healthy"
                if is_healthy
                else "unhealthy"
            ),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "environment": settings.ENVIRONMENT,
            "checks": {
                "database": (
                    "healthy"
                    if db_healthy
                    else "unhealthy"
                ),
            },
            "channels": {
                "email": (
                    "active"
                    if settings.GMAIL_ENABLED
                    else "disabled"
                ),
                "whatsapp": (
                    "active"
                    if settings.WHATSAPP_ENABLED
                    else "disabled"
                ),
                "web_form": (
                    "active"
                    if settings.WEBFORM_ENABLED
                    else "disabled"
                ),
            },
        },
    )


@app.get("/ready")
async def readiness_check():
    """
    Readiness check endpoint.
    """

    db_healthy = await check_db_health()

    is_ready = db_healthy

    status_code = (
        status.HTTP_200_OK
        if is_ready
        else status.HTTP_503_SERVICE_UNAVAILABLE
    )

    return JSONResponse(
        status_code=status_code,
        content={
            "ready": is_ready,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        },
    )


@app.get("/metrics")
async def metrics():
    """
    Basic application metrics.
    """

    return {
        "service": "custora_fte",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "metrics": {
            "requests_total": "TODO",
            "requests_duration_seconds": "TODO",
            "active_conversations": "TODO",
            "escalation_rate": "TODO",
        },
    }


# ============================================
# Router Inclusion
# ============================================

# Authentication API.
from src.api.auth import router as auth_router

app.include_router(
    auth_router,
    prefix="/api/v1",
)


# Channel handlers.
from src.api.channels import router as channels_router

app.include_router(channels_router)


# Ticket Management API.
from src.api.tickets import router as tickets_router

app.include_router(tickets_router)


# Admin API.
from src.api.admin import router as admin_router

app.include_router(admin_router)


# ============================================
# Development Server
# ============================================

if __name__ == "__main__":
    import uvicorn

    logger.info("Starting development server...")

    uvicorn.run(
        "src.api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.is_development,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True,
    )
