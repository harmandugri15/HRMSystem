"""
PULSE Enterprise AI People Analytics — Local Server Runner
Starts the FastAPI backend and serves the standalone Fireart Studio web app on http://localhost:8000.
"""

import uvicorn
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

if __name__ == "__main__":
    print("=" * 65)
    print("🔥 PULSE // Enterprise AI People Analytics Platform")
    print("   Starting native web application on http://localhost:8000")
    print("=" * 65)
    uvicorn.run("app.api.main:app", host="127.0.0.1", port=8000, reload=True)
