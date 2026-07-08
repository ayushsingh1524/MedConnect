import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import get_settings

from app.routers import auth, hcps, interactions, dashboard, chat

# Configure application logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Retrieve configuration
settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan events for FastAPI.
    Executed once when the application starts up and shuts down.
    """
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    # Startup tasks like initializing ML models, caches, etc. go here.
    yield
    # Shutdown tasks go here.
    logger.info("Shutting down application")

# Initialize the FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Production-ready FastAPI backend for MedConnect CRM.",
    lifespan=lifespan,
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc" # ReDoc UI
)

# Configure CORS Middleware
# Essential for allowing frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
)

# --- Router Registration ---
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(hcps.router, prefix="/api/v1/hcps", tags=["HCPs"])
app.include_router(interactions.router, prefix="/api/v1/interactions", tags=["Interactions"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["AI Chat"])

# --- Global Endpoints ---

@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint to verify the API is reachable.
    """
    return {"message": f"Welcome to {settings.APP_NAME} API"}

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for load balancers and container orchestrators.
    """
    return JSONResponse(
        content={
            "status": "healthy",
            "version": settings.APP_VERSION,
            "name": settings.APP_NAME
        },
        status_code=200
    )
