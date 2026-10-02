"""
render_traffic_monitor.py — Cloud-hosted real-time traffic monitor for Render.com
==================================================================================
A standalone Flask web app that:
  - Connects to MongoDB for persistent data
  - Serves the real-time traffic monitor page
  - Provides REST API for stats + activity history
  - Streams live events via Server-Sent Events (SSE)

This file is ONLY for the Render deployment (web monitor page).
The Telegram bot itself continues to run on your local Windows server.
The bot pushes events to MongoDB; this app reads from the same DB.

Render Setup:
  1. Create a MongoDB Atlas cluster (free tier)
  2. Get the connection string URI
  3. Set MONGODB_URI environment variable in Render web service settings
  4. Deploy this repo to Render (set start command: gunicorn render_traffic_monitor:app)
"""

import os
import json
import time
import threading
import queue as queue_module
from datetime import datetime
from pathlib import Path

# ── Optional pymongo / fallback ──────────────────────────────────────────────
try:
    import pymongo
    _HAS_MONGO = True
except ImportError:
    _HAS_MONGO = False

from flask import Flask, Response, jsonify, send_from_directory
from bson.objectid import ObjectId
from pymongo import MongoClient

app = Flask(__name__, static_folder=None)

# ── Database URL (set in Render environment) ───────────────────────────────────
MONGODB_URI = os.environ.get("MONGODB_URI", "")


def _get_db():
    if not _HAS_MONGO or not MONGODB_URI:
        raise RuntimeError("MongoDB not configured (MONGODB_URI missing or pymongo not installed)")
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=2000)
    return client.get_default_database("trading_bot_db")


def get_traffic_stats() -> dict:
    try:
        db = _get_db()
        users_col = db.users
        activity_col = db.activity_log
        positions_col = db.positions
        deposits_col = db.deposits
        
        # In a full mongo port, we would read these collections. 
        # But if the bot is still using SQLite for the main state and only Mongo for activity_log,
        # we might not have users/positions/deposits in Mongo. 
        # For this example, let's assume we can fetch stats from activity log as an approximation, 
        # or we just return the activity counts if the full bot isn't syncing everything to mongo.
        
        # We will attempt to get counts if the collections exist.
        total = users_col.count_documents({})
        
        from datetime import datetime, timedelta
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        one_hour_ago = (datetime.utcnow() - timedelta(hours=1)).isoformat()
        
        active = activity_col.distinct("user_id", {"ts": {"$gte": today_start}})
        
        events = activity_col.count_documents({"ts": {"$gte": today_start}})
        
        # If positions/deposits aren't in mongo, this will just be 0
        positions = positions_col.count_documents({"status": "OPEN"})
        pending = deposits_col.count_documents({"status": "PENDING"})
        
        return {
            "total_users": total, "active_today": len(active),
            "new_today": 0, "new_hour": 0, # harder to estimate without users collection
            "events_today": events, "open_positions": positions,
            "pending_deposits": pending,
        }
    except Exception as e:
        return {"error": str(e)}


def get_recent_activity(limit: int = 100) -> list:
    try:
        db = _get_db()
        activity_col = db.activity_log
        
        rows = activity_col.find().sort("_id", pymongo.DESCENDING).limit(limit)
        
        results = []
        for row in reversed(list(rows)):
            row["_id"] = str(row["_id"]) # Convert ObjectId to string for JSON
            results.append(row)
        return results
    except Exception as e:
        return []


# ── SSE subscriber pool ────────────────────────────────────────────────────────
_subscribers: list = []
_sub_lock = threading.Lock()


def _broadcast(payload: dict):
    with _sub_lock:
        dead = []
        for q in _subscribers:
            try:
                q.put_nowait(payload)
            except Exception:
                dead.append(q)
        for q in dead:
            _subscribers.remove(q)


# ── Poll MongoDB for new rows and push to SSE ───────────────────────────────
_last_seen_id = [None]  # mutable container for thread

def _poll_loop():
    """Background thread: polls activity_log every 2 seconds for new rows."""
    import time
    while True:
        try:
            db = _get_db()
            activity_col = db.activity_log
            
            query = {}
            if _last_seen_id[0]:
                query = {"_id": {"$gt": ObjectId(_last_seen_id[0])}}
            
            rows = activity_col.find(query).sort("_id", pymongo.ASCENDING).limit(50)
            
            for row in rows:
                _last_seen_id[0] = str(row["_id"])
                row["_id"] = str(row["_id"])
                _broadcast(row)
        except Exception:
            pass
        time.sleep(2)

# Start background poll thread
_t = threading.Thread(target=_poll_loop, daemon=True)
_t.start()


# ── Serve max seen id on startup ───────────────────────────────────────────────
def _init_last_seen():
    try:
        db = _get_db()
        activity_col = db.activity_log
        last_doc = activity_col.find_one(sort=[("_id", pymongo.DESCENDING)])
        if last_doc:
            _last_seen_id[0] = str(last_doc["_id"])
    except Exception:
        pass

_init_last_seen()


# ── Routes ─────────────────────────────────────────────────────────────────────
MONITOR_DIR = Path(__file__).resolve().parent / "monitor"

@app.route("/")
def index():
    return send_from_directory(str(MONITOR_DIR), "index.html")

@app.route("/api/stats")
def api_stats():
    return jsonify(get_traffic_stats())

@app.route("/api/activity")
def api_activity():
    return jsonify(get_recent_activity(100))


@app.route("/api/clients")
def api_clients():
    """Return per-user deposit summary: total deposited, deposit count, last seen."""
    try:
        db = _get_db()
        activity_col = db.activity_log

        # Get all events to build per-user profile
        rows = list(activity_col.find({}, {
            "user_id": 1, "username": 1, "first_name": 1,
            "event_type": 1, "detail": 1, "ts": 1, "lang": 1
        }).sort("_id", pymongo.DESCENDING).limit(5000))

        clients = {}
        for row in rows:
            uid = row.get("user_id")
            if not uid:
                continue
            uid = str(uid)
            if uid not in clients:
                clients[uid] = {
                    "user_id": uid,
                    "first_name": row.get("first_name", ""),
                    "username": row.get("username", ""),
                    "lang": row.get("lang", ""),
                    "last_seen": row.get("ts", ""),
                    "total_deposited": 0.0,
                    "deposit_count": 0,
                    "deposits": [],
                    "total_withdrawn": 0.0,
                    "withdrawal_count": 0,
                    "withdrawals": [],
                }
            # Deposits
            if row.get("event_type") == "deposit":
                detail = row.get("detail", "")
                ts = row.get("ts", "")
                try:
                    amt_str = detail.split("$")[1].split(" ")[0].replace(",", "")
                    amt = float(amt_str)
                    clients[uid]["total_deposited"] += amt
                    clients[uid]["deposit_count"] += 1
                    clients[uid]["deposits"].append({"amount": amt, "detail": detail, "ts": ts})
                except Exception:
                    pass
            # Withdrawals
            elif row.get("event_type") == "withdraw":
                detail = row.get("detail", "")
                ts = row.get("ts", "")
                try:
                    amt_str = detail.split("$")[1].split(" ")[0].replace(",", "")
                    amt = float(amt_str)
                    clients[uid]["total_withdrawn"] += amt
                    clients[uid]["withdrawal_count"] += 1
                    clients[uid]["withdrawals"].append({"amount": amt, "detail": detail, "ts": ts})
                except Exception:
                    pass

        # Add net balance and sort by total deposited descending
        for c in clients.values():
            c["net_balance"] = c["total_deposited"] - c["total_withdrawn"]
        result = sorted(clients.values(), key=lambda x: x["total_deposited"], reverse=True)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/health")
def health():
    return jsonify({"status": "ok", "ts": datetime.utcnow().isoformat()})

@app.route("/stream")
def stream():
    def gen():
        q: queue_module.SimpleQueue = queue_module.SimpleQueue()
        with _sub_lock:
            _subscribers.append(q)
        try:
            last_hb = time.time()
            while True:
                try:
                    item = q.get(timeout=1.0)
                    yield f"data: {json.dumps(item)}\n\n"
                except Exception:
                    if time.time() - last_hb > 20:
                        yield ": heartbeat\n\n"
                        last_hb = time.time()
        except GeneratorExit:
            pass
        finally:
            with _sub_lock:
                try:
                    _subscribers.remove(q)
                except ValueError:
                    pass

    return Response(gen(), mimetype="text/event-stream", headers={
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",
        "Connection": "keep-alive",
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5001)), debug=False, threaded=True)
