"""
traffic_monitor.py — Real-time Client Traffic Monitor
======================================================
Standalone Flask web server that serves a live traffic monitor page.
Completely independent from the admin dashboard.

Run:
    py traffic_monitor.py

Then open in browser:
    http://localhost:5001
"""

import json
import time
import threading
from datetime import datetime
from pathlib import Path

from flask import Flask, Response, jsonify, send_from_directory

from activity_logger import (
    subscribe, unsubscribe, get_recent_activity, get_traffic_stats
)

# ─── App Setup ────────────────────────────────────────────────────────────────

app = Flask(__name__, static_folder=None)
MONITOR_DIR = Path(__file__).resolve().parent / "monitor"

# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Serve the monitor HTML page."""
    return send_from_directory(str(MONITOR_DIR), "index.html")


@app.route("/api/stats")
def api_stats():
    """Return current aggregate stats as JSON."""
    return jsonify(get_traffic_stats())


@app.route("/api/activity")
def api_activity():
    """Return last 100 activity events as JSON (for initial page load)."""
    return jsonify(get_recent_activity(100))


@app.route("/stream")
def stream():
    """
    Server-Sent Events endpoint.
    Browser connects once; server pushes events in real-time.
    """
    def event_generator():
        q = subscribe()
        try:
            # Send a heartbeat comment every 20 seconds to keep connection alive
            last_heartbeat = time.time()
            while True:
                try:
                    # Non-blocking check with 1-second poll interval
                    item = q.get(timeout=1.0)
                    data = json.dumps(item)
                    yield f"data: {data}\n\n"
                except Exception:
                    # Timeout — send heartbeat if due
                    if time.time() - last_heartbeat > 20:
                        yield ": heartbeat\n\n"
                        last_heartbeat = time.time()
        except GeneratorExit:
            pass
        finally:
            unsubscribe(q)

    return Response(
        event_generator(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        }
    )


# ─── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    print("=" * 60)
    print("  [MONITOR] Real-time Traffic Monitor")
    print("=" * 60)
    print(f"  Open in browser: http://localhost:5001")
    print(f"  Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("  Press Ctrl+C to stop.")
    print("=" * 60)
    app.run(
        host="0.0.0.0",
        port=5001,
        debug=False,
        threaded=True,
        use_reloader=False,
    )

