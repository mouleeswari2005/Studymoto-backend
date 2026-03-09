"""
Main FastAPI application.
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.api.rest import auth, tasks, exams, classes, pomodoro, preferences, dashboard, content, reminders, student, study_plans, summer_vacations, notes, streaks, notifications, push_subscriptions

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
# If CORS_ORIGINS is '*', we must use allow_origin_regex or remove allow_credentials
# because allow_origins=['*'] is not allowed with allow_credentials=True
cors_origins = settings.cors_origins_list.copy()

# Ensure common development and production origins are always present
for default_origin in ["http://localhost:5173", "http://127.0.0.1:5173", "https://study-moto.vercel.app"]:
    if default_origin not in cors_origins:
        cors_origins.append(default_origin)

# Remove '*' from origins if it exists to prevent credentials error
use_all_origins = "*" in cors_origins
if use_all_origins:
    cors_origins = [o for o in cors_origins if o != "*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins if not use_all_origins else ["*"],
    allow_origin_regex=None if not use_all_origins else "https://.*\.vercel\.app", # Allow Vercel preview URLs if * is set
    allow_credentials=not use_all_origins, # Credentials must be False if using '*'
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(exams.router)
app.include_router(classes.router)
app.include_router(pomodoro.router)
app.include_router(preferences.router)
app.include_router(dashboard.router)
app.include_router(content.router)
app.include_router(reminders.router)
app.include_router(student.router)
app.include_router(study_plans.router)
app.include_router(summer_vacations.router)
app.include_router(notes.router)
app.include_router(streaks.router)
app.include_router(notifications.router)
app.include_router(push_subscriptions.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Student Productivity API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.on_event("startup")
async def startup_event():
    """Start background tasks on application startup."""
    from app.services.notification_worker import notification_worker
    await notification_worker.start()
    logging.info("Background notification worker started")


@app.on_event("shutdown")
async def shutdown_event():
    """Stop background tasks on application shutdown."""
    from app.services.notification_worker import notification_worker
    await notification_worker.stop()
    logging.info("Background notification worker stopped")

