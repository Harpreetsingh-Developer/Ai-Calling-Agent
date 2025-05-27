#!/usr/bin/env python3
"""
Main application entry point for the AI Calling Agent system.
This file initializes all components and starts the FastAPI server.
"""
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.router import api_router
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.services.asterisk.ami_client import AsteriskAMIClient
from app.services.rasa.client import RasaClient

# Setup logging
logger = setup_logging()

# Initialize FastAPI app
app = FastAPI(
    title="AI Calling Agent",
    description="An AI-powered calling agent with multi-language support",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include API routers
app.include_router(api_router, prefix="/api")

# Event handlers for database connection
@app.on_event("startup")
async def startup_db_client():
    """Connect to MongoDB on startup."""
    logger.info("Connecting to MongoDB...")
    await connect_to_mongo()
    logger.info("Connected to MongoDB")
    
    # Initialize Asterisk AMI client
    logger.info("Connecting to Asterisk AMI...")
    try:
        ami_client = AsteriskAMIClient()
        await ami_client.connect()
        app.state.ami_client = ami_client
        logger.info("Connected to Asterisk AMI")
    except Exception as e:
        logger.error(f"Failed to connect to Asterisk AMI: {e}")
    
    # Initialize Rasa client
    app.state.rasa_client = RasaClient()
    logger.info("Rasa client initialized")

@app.on_event("shutdown")
async def shutdown_db_client():
    """Close MongoDB connection on shutdown."""
    logger.info("Disconnecting from MongoDB...")
    await close_mongo_connection()
    logger.info("Disconnected from MongoDB")
    
    # Close Asterisk AMI connection
    if hasattr(app.state, "ami_client"):
        logger.info("Disconnecting from Asterisk AMI...")
        await app.state.ami_client.disconnect()
        logger.info("Disconnected from Asterisk AMI")

@app.get("/")
async def root():
    """Root endpoint that returns a basic welcome message."""
    return {"message": "Welcome to AI Calling Agent API. Visit /docs for API documentation."}

if __name__ == "__main__":
    """Run the application using uvicorn server."""
    uvicorn.run(
        "app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    ) 