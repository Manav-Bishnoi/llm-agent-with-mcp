#!/usr/bin/env python3
"""
Startup script for the Multi-Agent AI System
Initializes the database and starts the FastAPI server
"""

import uvicorn
import os
import sys
from backend.core.context_manager import ContextManager

def init_database():
    """Initialize the database and create necessary tables"""
    try:
        context_manager = ContextManager()
        context_manager.init_db()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def check_dependencies():
    """Check if all required dependencies are available"""
    required_modules = [
        'fastapi',
        'uvicorn',
        'requests',
        'sqlalchemy',
        'pydantic'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"❌ Missing required modules: {', '.join(missing_modules)}")
        print("Please install them using: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are available")
    return True

def main():
    """Main startup function"""
    print("🚀 Starting Multi-Agent AI System...")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Initialize database
    if not init_database():
        sys.exit(1)
    
    # Start the server
    print("🌐 Starting FastAPI server on http://localhost:8000")
    print("📱 Frontend available at http://localhost:8000/frontend/")
    print("🔧 API documentation at http://localhost:8000/docs")
    print("💚 Health check at http://localhost:8000/health")
    print("\nPress Ctrl+C to stop the server")
    
    try:
        uvicorn.run(
            "app:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 