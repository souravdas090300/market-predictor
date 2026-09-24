"""
Entry point for Railway deployment.
This file allows Railway to detect the Python project at the root level.
The actual application is in the market-predictor subdirectory.
"""

import os
import sys

# Add the market-predictor directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'market-predictor'))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.api:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
