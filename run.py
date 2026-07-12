import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))
from app import app

if __name__ == "__main__":
    port = int(os.getenv("PORT", os.getenv("FLASK_PORT", "5100")))
    app.run(host="0.0.0.0", port=port, debug=False)