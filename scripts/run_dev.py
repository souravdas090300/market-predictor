"""Start the application in development mode."""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load development environment
from scripts.load_env import load_env
load_env("development")

# Import and start the app
import uvicorn

if __name__ == "__main__":
    print("Starting Market Predictor in DEVELOPMENT mode...")
    print(f"Environment: {os.getenv('ENV', 'development')}")
    print(f"Debug Mode: {os.getenv('ENABLE_DEBUG_MODE', 'false')}")
    print(f"Log Level: {os.getenv('LOG_LEVEL', 'INFO')}")
    print(f"Server: http://localhost:8000")
    print(f"Admin: http://localhost:8000/admin")
    print()
    
    uvicorn.run(
        "app.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=os.getenv('LOG_LEVEL', 'debug').lower()
    )
