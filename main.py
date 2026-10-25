"""
HireWise AI - Root Application Launcher.
Provides a convenient entrypoint to start the FastAPI backend server.
"""

import sys
from pathlib import Path
import uvicorn

# Ensure backend directory is in python search path
backend_dir = str(Path(__file__).parent / "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)


def main():
    print("=" * 60)
    print("Starting HireWise AI Backend Server (FastAPI + Uvicorn)")
    print("=" * 60)
    print("API Documentation: http://127.0.0.1:8000/docs")
    print("Health Check:      http://127.0.0.1:8000/health")
    print("=" * 60)
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()
