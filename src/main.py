# main.py - Application Entry Point (Spring Boot Main Class equivalent)

from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import uvicorn
import os

from database import engine, get_db
from models import Base
from controllers import bible_router
from config import settings

# Create FastAPI app (equivalent to @SpringBootApplication)
app = FastAPI(
    title="Bible App",
    description="A simple Bible application - Python equivalent of Spring Boot",
    version="1.0.0",
    docs_url="/swagger",
    redoc_url="/redoc"
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Setup templates
templates = Jinja2Templates(directory="templates")

# Create templates directory if it doesn't exist
os.makedirs("templates", exist_ok=True)

# Include routers (equivalent to @RestController registration)
app.include_router(bible_router, prefix="/api/v1", tags=["bible"])

# ============================================================================
# Error Handlers (Spring Boot @ExceptionHandler equivalent)
# ============================================================================

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle ValueError exceptions"""
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=str(exc)
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Internal server error"
    )

# Root endpoint with UI
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": "Bible App"})

# Health check endpoint (Spring Boot Actuator style)
@app.get("/health")
async def health_check():
    return {"status": "UP", "version": "1.0.0", "application": "Bible App"}

# Additional info endpoint
@app.get("/info")
async def app_info():
    return {
        "name": "Bible App",
        "version": "1.0.0",
        "description": "Python Bible application with FastAPI",
        "framework": "FastAPI",
        "database": "SQLite",
        "endpoints": {
            "ui": "/",
            "api_docs": "/swagger",
            "health": "/health"
        }
    }

if __name__ == "__main__":
    print("Starting Bible App...")
    print(f"API Documentation: http://localhost:8080/swagger")
    print(f"Web Interface: http://localhost:8080/")
    print(f"Health Check: http://localhost:8080/health")
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
