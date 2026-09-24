"""Run the admin API server on a separate port."""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import uvicorn

if __name__ == "__main__":
    # Run admin API on port 8001
    uvicorn.run(
        "app.admin_api:admin_app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )