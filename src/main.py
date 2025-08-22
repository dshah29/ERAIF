#!/usr/bin/env python3
"""
ERAIF Main Application Entry Point

This module provides the main entry point for the ERAIF emergency radiology
AI interoperability framework.
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .eraif_core import ERAIFCore
from .utils.config import load_config
from .utils.logging import setup_logging


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="ERAIF - Emergency Radiology AI Interoperability Framework",
        description="Vendor-neutral framework for medical imaging system interoperability during emergencies",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    return app


async def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(description="ERAIF Emergency Connector")
    parser.add_argument(
        "--config",
        type=str,
        default="config.yml",
        help="Path to configuration file"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind to"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port to bind to"
    )
    parser.add_argument(
        "--emergency-mode",
        action="store_true",
        help="Start in emergency mode"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(level=args.log_level)
    logger = logging.getLogger(__name__)
    
    try:
        # Load configuration
        config_path = Path(args.config)
        if config_path.exists():
            config = load_config(config_path)
            logger.info(f"Loaded configuration from {config_path}")
        else:
            logger.warning(f"Configuration file {config_path} not found, using defaults")
            config = {}
        
        # Initialize ERAIF Core
        eraif_core = ERAIFCore(config)
        
        # Set emergency mode if requested
        if args.emergency_mode:
            logger.warning("Starting in EMERGENCY MODE")
            await eraif_core.activate_emergency_mode("Manual startup activation")
        
        # Create FastAPI app
        app = create_app()
        
        # Register ERAIF core with the app
        app.state.eraif_core = eraif_core
        
        # Add startup and shutdown events
        @app.on_event("startup")
        async def startup_event():
            logger.info("ERAIF Emergency Connector starting up...")
            await eraif_core.initialize()
            logger.info("ERAIF Emergency Connector ready!")
        
        @app.on_event("shutdown")
        async def shutdown_event():
            logger.info("ERAIF Emergency Connector shutting down...")
            await eraif_core.shutdown()
            logger.info("ERAIF Emergency Connector stopped.")
        
        # Health check endpoint
        @app.get("/health")
        async def health_check():
            return await eraif_core.get_health_status()
        
        # Emergency status endpoint
        @app.get("/emergency/status")
        async def emergency_status():
            return await eraif_core.get_emergency_status()
        
        # Emergency activation endpoint
        @app.post("/emergency/activate")
        async def activate_emergency(request: dict):
            reason = request.get("reason", "Manual activation")
            return await eraif_core.activate_emergency_mode(reason)
        
        # Emergency test endpoint
        @app.post("/emergency/test")
        async def test_emergency():
            return await eraif_core.test_emergency_systems()
        
        # Start the server
        logger.info(f"Starting ERAIF server on {args.host}:{args.port}")
        
        config_server = uvicorn.Config(
            app,
            host=args.host,
            port=args.port,
            log_level=args.log_level.lower(),
            access_log=True
        )
        
        server = uvicorn.Server(config_server)
        await server.serve()
        
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
