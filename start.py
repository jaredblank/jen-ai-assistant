#!/usr/bin/env python3
"""
Jen AI Assistant - Startup Script
Comprehensive voice-enabled real estate AI assistant
"""

import os
import sys
import asyncio
import logging
from datetime import datetime

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def setup_logging():
    """Configure logging for the application"""
    
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(logs_dir, exist_ok=True)
    
    # Configure logging
    log_filename = os.path.join(logs_dir, f"jen_{datetime.now().strftime('%Y%m%d')}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific loggers
    logging.getLogger("jen").setLevel(logging.INFO)
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    
    return logging.getLogger("jen.startup")

async def health_check():
    """Perform comprehensive health check before starting"""
    
    log = logging.getLogger("jen.startup")
    
    try:
        # Test database connection
        from database_service import db_service
        db_healthy = await db_service.health_check()
        log.info(f"Database health: {'OK' if db_healthy else 'FAILED'}")
        
        # Test AI service
        from ai_service import jen_ai
        ai_healthy = jen_ai.health_check()
        log.info(f"AI service health: {'OK' if ai_healthy else 'FAILED'}")
        
        # Test voice service
        from voice_service import voice_processor
        voice_healthy = voice_processor.health_check()
        log.info(f"Voice service health: {'OK' if voice_healthy else 'FAILED'}")
        
        if not all([db_healthy, ai_healthy, voice_healthy]):
            log.error("Health check failed - some services are not available")
            return False
            
        log.info("All services healthy - ready to start!")
        return True
        
    except Exception as e:
        log.error(f"Health check failed with error: {e}")
        return False

def main():
    """Main startup function"""
    
    log = setup_logging()
    log.info("Starting Jen AI Assistant...")
    log.info("=" * 50)
    
    # Display startup banner
    print("""
    ==========================================
             JEN AI ASSISTANT
       Voice-Enabled Real Estate AI
                                      
       * Voice Queries                   
       * Live Database Access            
       * Phone Integration               
       * Natural Language Processing     
    ==========================================
    """)
    
    # Perform health check
    try:
        health_ok = asyncio.run(health_check())
        if not health_ok:
            log.error("Startup aborted due to health check failures")
            sys.exit(1)
    except Exception as e:
        log.error(f"Health check crashed: {e}")
        sys.exit(1)
    
    # Start the FastAPI server
    log.info("Starting FastAPI server...")
    
    try:
        import uvicorn
        from main import app
        
        # Get configuration
        host = os.getenv("HOST", "0.0.0.0")
        port = int(os.getenv("PORT", "8000"))
        workers = int(os.getenv("MAX_WORKERS", "1"))
        
        log.info(f"Server starting on {host}:{port} with {workers} worker(s)")
        
        # Start server
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            workers=workers,
            reload=os.getenv("ENVIRONMENT", "development") == "development",
            log_level="info",
            access_log=True
        )
        
    except KeyboardInterrupt:
        log.info("Server shutdown requested by user")
    except Exception as e:
        log.error(f"Server startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()