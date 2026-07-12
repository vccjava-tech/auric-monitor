"""Flask server for Gold-Silver Macro Monitor."""
from flask import Flask, jsonify, send_from_directory
from data_sources import fetch_all
import os, sys

app = Flask(__name__, static_folder="../frontend", static_url_path="")

@app.route("/")
def index():
    return send_from_directory("../frontend", "index.html")

@app.route("/api/data")
def api_data():
    try:
        return jsonify(fetch_all())
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", "5100"))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    print(f"Auric Monitor: http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=debug)