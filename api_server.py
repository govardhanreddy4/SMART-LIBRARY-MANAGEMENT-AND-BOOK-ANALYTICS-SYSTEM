"""Launcher script for FastAPI Uvicorn REST API Server."""

import sys
from pathlib import Path
import uvicorn

# Ensure project root is in Python module search path
sys.path.insert(0, str(Path(__file__).resolve().parent))

if __name__ == "__main__":
    print("==================================================================")
    print(" Smart Library Management and Book Analytics System - REST API")
    print(" Backend Server running at: http://127.0.0.1:8000")
    print(" Interactive Swagger Docs at: http://127.0.0.1:8000/docs")
    print("==================================================================")
    uvicorn.run("server.app:app", host="127.0.0.1", port=8000, reload=False)
