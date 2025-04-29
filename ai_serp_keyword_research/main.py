"""
AI SERP Keyword Research Agent for POD Graphic Tees

This module serves as the main entry point for the application.
It initializes the FastAPI app and configures routes, middleware, and dependencies.
"""

import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="AI SERP Keyword Research Agent",
    description="""
    Analyze Google Search Engine Results Pages (SERPs) for POD graphic tees, 
    extract key SEO insights, and recommend targeted optimization strategies.
    
    The API provides endpoints for keyword analysis, feedback collection, and system health monitoring.
    """,
    version="1.0.0",
    docs_url=None,  # Disable default docs to use custom ones
    redoc_url=None,  # Disable default redoc to use custom one
)

# Import components after app creation to avoid circular imports
from ai_serp_keyword_research.api import create_api_router
from ai_serp_keyword_research.api.middleware.auth import APIKeyMiddleware
from ai_serp_keyword_research.api.middleware.rate_limiter import RateLimitMiddleware
from ai_serp_keyword_research.api.middleware.tracing import TracingMiddleware
from ai_serp_keyword_research.api.middleware.metrics_middleware import MetricsMiddleware
from ai_serp_keyword_research.api.middleware.logging_middleware import RequestLoggingMiddleware, ContextualLoggingMiddleware
from ai_serp_keyword_research.api.middleware.security import SecurityMiddleware
from ai_serp_keyword_research.api.routes.health import router as health_router
from ai_serp_keyword_research.services.cache import create_cache_service
from ai_serp_keyword_research.data.repositories.base import create_db_session
from ai_serp_keyword_research.tracing import configure_tracing, trace
from ai_serp_keyword_research.metrics import configure_metrics
from ai_serp_keyword_research.metrics.performance import get_performance_monitor
from ai_serp_keyword_research.utils.logging import app_logger
from ai_serp_keyword_research.utils.env_validator import validate_environment, EnvironmentValidationError
from ai_serp_keyword_research.security import get_credential_manager

# Validate required environment variables
try:
    env_vars = validate_environment([
        {"name": "DATABASE_URL", "type": "url", "required": False, "allowed_schemes": ["postgresql", "sqlite"]},
        {"name": "REDIS_URL", "type": "url", "required": False, "allowed_schemes": ["redis"]},
        {"name": "SERP_API_KEY", "type": "api_key", "required": False, "min_length": 8},
        {"name": "OPENAI_API_KEY", "type": "api_key", "required": False, "min_length": 8},
        {"name": "RATE_LIMIT_PER_MINUTE", "type": "int", "required": False, "default": 60, "min_value": 1},
        {"name": "RATE_LIMIT_PER_DAY", "type": "int", "required": False, "default": 1000, "min_value": 1},
        {"name": "API_KEYS", "type": "list", "required": False, "default": ["dev-api-key-1234"]},
        {"name": "CORS_ORIGINS", "type": "list", "required": False, "default": ["*"]},
        {"name": "LOG_LEVEL", "type": "str", "required": False, "default": "INFO"},
        {"name": "ENVIRONMENT", "type": "str", "required": False, "default": "development"}
    ])
    app_logger.info("Environment validation successful")
except EnvironmentValidationError as e:
    app_logger.error(f"Environment validation failed: {str(e)}")
    raise

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure API-specific middleware (in order of execution)
app.add_middleware(ContextualLoggingMiddleware)  # Must be first to set up correlation ID
app.add_middleware(RequestLoggingMiddleware, 
                  log_request_body=os.getenv("LOG_REQUEST_BODY", "false").lower() == "true")
app.add_middleware(TracingMiddleware)
app.add_middleware(
    MetricsMiddleware,
    exempt_paths=["/health", "/docs", "/openapi.json", "/redoc", "/metrics"]
)
app.add_middleware(
    SecurityMiddleware,
    exempt_paths=["/health", "/docs", "/openapi.json", "/redoc", "/metrics"]
)
app.add_middleware(
    APIKeyMiddleware,
    api_keys=os.getenv("API_KEYS", "").split(",") if os.getenv("API_KEYS") else None,
    exempt_paths=["/health", "/docs", "/openapi.json", "/redoc", "/metrics"]
)
app.add_middleware(
    RateLimitMiddleware,
    rate_limit_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "60")),
    rate_limit_per_day=int(os.getenv("RATE_LIMIT_PER_DAY", "1000")),
    exempt_paths=["/health", "/docs", "/openapi.json", "/redoc", "/metrics"]
)

# Include routers
app.include_router(create_api_router(), prefix="/api/v1")
app.include_router(health_router)

# Custom OpenAPI and documentation endpoints
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Generate custom Swagger UI for API documentation."""
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )

@app.get("/redoc", include_in_schema=False)
async def custom_redoc_html():
    """Generate custom ReDoc for API documentation."""
    return get_redoc_html(
        openapi_url="/openapi.json",
        title=app.title + " - ReDoc",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
    )

@app.get("/openapi.json", include_in_schema=False)
async def get_open_api_endpoint():
    """Generate OpenAPI schema."""
    return get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

# Define dependency providers
@app.on_event("startup")
async def startup_event():
    """Initialize resources on application startup."""
    # Initialize credential manager
    credential_manager = get_credential_manager()
    app.state.credential_manager = credential_manager
    
    # Initialize database tables if configured
    init_db = os.getenv("INIT_DB", "false").lower() == "true"
    if init_db:
        from ai_serp_keyword_research.data import create_database_tables
        await create_database_tables()
    
    # Set up cache service
    cache_url = credential_manager.get_credential("REDIS", {}).get("url") or os.getenv("REDIS_URL", "redis://localhost:6379/0")
    app.state.cache_service = await create_cache_service(cache_url)
    
    # Set up database session
    db_url = credential_manager.get_connection_string("DATABASE") or os.getenv("DATABASE_URL", "sqlite:///./test.db")
    app.state.db_session = await create_db_session(db_url)
    
    # Set up tracing
    configure_tracing_enabled = os.getenv("ENABLE_TRACING", "false").lower() == "true"
    if configure_tracing_enabled:
        configure_tracing()
    
    # Set up metrics collection
    metrics_enabled = os.getenv("ENABLE_METRICS", "false").lower() == "true"
    if metrics_enabled:
        from ai_serp_keyword_research.metrics.exporters import ConsoleExporter, LoggingExporter
        
        # Configure metrics exporters based on environment
        exporters = [ConsoleExporter()]
        
        # Add logging exporter in production
        if os.getenv("ENVIRONMENT", "development") == "production":
            exporters.append(LoggingExporter())
        
        # Add Prometheus exporter if configured
        prometheus_enabled = os.getenv("ENABLE_PROMETHEUS", "false").lower() == "true"
        if prometheus_enabled:
            from ai_serp_keyword_research.metrics.exporters import PrometheusExporter
            
            # Get Prometheus configuration
            prometheus_port = int(os.getenv("PROMETHEUS_PORT", "9090"))
            prometheus_path = os.getenv("PROMETHEUS_PATH", "/metrics")
            prometheus_push_gateway = os.getenv("PROMETHEUS_PUSH_GATEWAY")
            
            # Create exporter
            exporters.append(
                PrometheusExporter(
                    namespace="serp_keyword_agent",
                    expose_port=prometheus_port,
                    expose_path=prometheus_path,
                    push_gateway=prometheus_push_gateway
                )
            )
        
        # Configure metrics with exporters
        configure_metrics(exporters)
        app_logger.info("Metrics collection configured with %d exporters", len(exporters))
        
        # Start performance metrics monitor if enabled
        performance_metrics_enabled = os.getenv("ENABLE_PERFORMANCE_METRICS", "false").lower() == "true"
        if performance_metrics_enabled:
            interval = int(os.getenv("PERFORMANCE_METRICS_INTERVAL", "60"))
            performance_monitor = get_performance_monitor(interval=interval)
            performance_monitor.start()
            app.state.performance_monitor = performance_monitor
            app_logger.info("Performance metrics monitor started with interval %d seconds", interval)
    
    # Run initial security scan in development mode
    if os.getenv("ENVIRONMENT", "development") == "development" and os.getenv("SECURITY_SCAN_ON_START", "false").lower() == "true":
        import threading
        from ai_serp_keyword_research.security.security_review import run_security_review
        
        def run_scan():
            try:
                run_security_review(output_file="security-report.json")
            except Exception as e:
                app_logger.error(f"Failed to run security scan: {str(e)}")
        
        # Run in a separate thread to not block startup
        threading.Thread(target=run_scan).start()
        app_logger.info("Security scan started in background")

# Define shutdown handlers
@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on application shutdown."""
    # Close Redis connections
    if hasattr(app.state, "cache_service"):
        await app.state.cache_service.close()
    
    # Close database connections
    if hasattr(app.state, "db_session"):
        await app.state.db_session.close()
    
    # Stop performance metrics monitor if running
    if hasattr(app.state, "performance_monitor"):
        app.state.performance_monitor.stop()
    
    # Close any other resources
    with trace("application_shutdown"):
        pass  # Any additional cleanup can be added here

# Dependency injection helpers
def get_cache_service():
    """Get the cache service for dependency injection."""
    return app.state.cache_service

def get_db_session():
    """Get the database session for dependency injection."""
    return app.state.db_session

def get_credentials():
    """Get the credential manager for dependency injection."""
    return app.state.credential_manager 