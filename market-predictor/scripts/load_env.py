"""Load environment variables from a specific environment file."""
import os
from pathlib import Path
from dotenv import load_dotenv

def load_env(env: str = "development"):
    """
    Load environment variables from .env.{env} file.
    
    Args:
        env: Environment name (development or production)
    """
    # Get the project root
    root = Path(__file__).parent.parent
    
    # Load the specific environment file
    env_file = root / f".env.{env}"
    
    if env_file.exists():
        load_dotenv(env_file)
        print(f"Loaded environment: {env}")
    else:
        print(f"Warning: {env_file} not found, using defaults")
    
    # Set ENV variable if not already set
    if not os.getenv("ENV"):
        os.environ["ENV"] = env

if __name__ == "__main__":
    import sys
    
    env = sys.argv[1] if len(sys.argv) > 1 else "development"
    load_env(env)
