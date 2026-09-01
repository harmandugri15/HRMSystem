"""
PULSE Enterprise AI People Analytics — Production Server Runner
Supports local development and cloud hosting (Render, Railway, Fly.io, AWS, Docker).
"""

import os
import uvicorn
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    print("=" * 65)
    print("🔥 PULSE // Enterprise AI People Analytics Platform")
    print(f"   Server listening on http://{host}:{port}")
    print("=" * 65)
    uvicorn.run("app.api.main:app", host=host, port=port, reload=False)
