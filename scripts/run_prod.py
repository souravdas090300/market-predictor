"""Start the application in production mode."""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load production environment
from scripts.load_env import load_env
load_env("production")

# Import and start the app
import uvicorn
from app.api import app

if __name__ == "__main__":
    print("Starting Market Predictor in PRODUCTION mode...")
    print(f"Environment: {os.getenv('ENV', 'production')}")
    print(f"Debug Mode: {os.getenv('ENABLE_DEBUG_MODE', 'false')}")
    print(f"Log Level: {os.getenv('LOG_LEVEL', 'INFO')}")
    print(f"Server: http://localhost:8000")
    print(f"Admin: http://localhost:8000/admin")
    print()
    
    # Production settings
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False,  # No auto-reload in production
        workers=4,  # Multiple workers for production
        log_level=os.getenv('LOG_LEVEL', 'info').lower(),
        access_log=True
    )
