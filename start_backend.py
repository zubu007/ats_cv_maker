#!/usr/bin/env python3
"""
Start the ATS CV Maker backend API server
"""

import uvicorn
import os
from pathlib import Path

if __name__ == "__main__":
    # Set the working directory to the project root
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Start the server
    uvicorn.run(
        "backend.src.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
