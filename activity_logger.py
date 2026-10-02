"""
activity_logger.py — Shared in-memory activity event queue for the real-time traffic monitor.

Bot handlers call `push_event()` to emit events.
The Flask SSE endpoint in traffic_monitor.py reads from `event_queue`.
"""

import queue
import json
import time
import sqlite3
from datetime import datetime
from pathlib import Path

# Lazy import to avoid circular dependency
_channel_notifier = None

def _get_notifier():
    global _channel_notifier
    if _channel_notifier is None:
        try:
            import channel_notifier
            _channel_notifier = channel_notifier
        except Exception:
            pass
    return _channel_notifier

# ---------------------------------------------------------------------------
# In-memory event queue (thread-safe)
# Subscribers hold their own SimpleQueue that receives copies of each event.
# ---------------------------------------------------------------------------

_subscribers: list = []   # list of queue.SimpleQueue

def subscribe() -> queue.SimpleQueue:
    """Register a new SSE subscriber and return their dedicated queue."""
    q: queue.SimpleQueue = queue.SimpleQueue()
    _subscribers.append(q)
    return q

def unsubscribe(q: queue.SimpleQueue):
    """Remove a subscriber queue."""
    try:
        _subscribers.remove(q)
    except ValueError:
        pass

def push_event(event_type: str, data: dict):
    """
    Broadcast an event to all live SSE subscribers AND persist it to the DB.

    event_type examples:
        'new_user'    — first-time /start
        'returning'   — existing user /start
        'command'     — any /command used
        'message'     — text message from reply keyboard
        'deposit'     — deposit request submitted
        'withdraw'    — withdrawal request submitted
        'trade_open'  — trade opened
        'trade_close' — trade closed
    """
    payload = {
        "type": event_type,
        "ts": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "epoch": int(time.time()),
        **data,
    }
    # Persist to DB
    _persist(payload)
    # Broadcast to local SSE clients
    for q in list(_subscribers):
        try:
            q.put_nowait(payload)
        except Exception:
            pass
    # Forward to Telegram private channel (if configured)
    try:
        notifier = _get_notifier()
        if notifier:
            notifier.dispatch(event_type, data)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# DB persistence — activity_log table
# ---------------------------------------------------------------------------

_DB_PATH = Path(__file__).resolve().parent / "trading_bot.db"


def _get_conn():
    conn = sqlite3.connect(_DB_PATH, timeout=20.0)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_activity_table():
    """Create the activity_log table if it doesn't exist."""
    with _get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS activity_log (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT    NOT NULL,
                user_id    INTEGER,
                username   TEXT,
                first_name TEXT,
                action     TEXT,
                detail     TEXT,
                ts         TEXT    NOT NULL,
                epoch      INTEGER NOT NULL
            )
        """)
        conn.commit()


def _persist(payload: dict):
    # ── Write to local SQLite ──────────────────────────────────────────────────
    try:
        with _get_conn() as conn:
            conn.execute("""
                INSERT INTO activity_log (event_type, user_id, username, first_name, action, detail, ts, epoch)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                payload.get("type"),
                payload.get("user_id"),
                payload.get("username"),
                payload.get("first_name"),
                payload.get("action"),
                payload.get("detail"),
                payload.get("ts"),
                payload.get("epoch"),
            ))
            conn.commit()
    except Exception:
        pass  # Never crash the bot over monitor logging

    # ── Also write to MongoDB (if MONGODB_URI is configured) ────────
    _persist_mongo(payload)


def _persist_mongo(payload: dict):
    """
    Dual-write to MongoDB so the cloud traffic monitor sees events.
    Only runs when MONGODB_URI env var is set.
    Install pymongo: pip install pymongo
    """
    import os
    db_url = os.environ.get("MONGODB_URI", "")
    if not db_url:
        return
    try:
        from pymongo import MongoClient
        client = MongoClient(db_url, serverSelectionTimeoutMS=2000)
        db = client.get_default_database("trading_bot_db")
        collection = db.activity_log
        
        # Prepare payload for mongo (no auto-increment ID needed, MongoDB handles _id)
        doc = {
            "event_type": payload.get("type"),
            "user_id": payload.get("user_id"),
            "username": payload.get("username"),
            "first_name": payload.get("first_name"),
            "action": payload.get("action"),
            "detail": payload.get("detail"),
            "ts": payload.get("ts"),
            "epoch": payload.get("epoch"),
            "lang": payload.get("lang"),
        }
        collection.insert_one(doc)
    except Exception:
        pass  # Never crash the bot





def get_recent_activity(limit: int = 100) -> list:
    """Fetch recent activity events from DB (for page load / catch-up)."""
    try:
        with _get_conn() as conn:
            rows = conn.execute("""
                SELECT * FROM activity_log
                ORDER BY id DESC LIMIT ?
            """, (limit,)).fetchall()
        return [dict(r) for r in reversed(rows)]
    except Exception:
        return []


def get_traffic_stats() -> dict:
    """Return aggregate stats for the monitor dashboard header."""
    try:
        with _get_conn() as conn:
            total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            active_today = conn.execute(
                "SELECT COUNT(*) FROM users WHERE date(last_active) = date('now')"
            ).fetchone()[0]
            new_today = conn.execute(
                "SELECT COUNT(*) FROM users WHERE date(created_at) = date('now')"
            ).fetchone()[0]
            new_hour = conn.execute(
                "SELECT COUNT(*) FROM users WHERE created_at >= datetime('now', '-1 hour')"
            ).fetchone()[0]
            events_today = conn.execute(
                "SELECT COUNT(*) FROM activity_log WHERE date(ts) = date('now')"
            ).fetchone()[0]
            open_positions = conn.execute(
                "SELECT COUNT(*) FROM positions WHERE status = 'OPEN'"
            ).fetchone()[0]
            pending_deposits = conn.execute(
                "SELECT COUNT(*) FROM deposits WHERE status = 'PENDING'"
            ).fetchone()[0]
        return {
            "total_users": total_users,
            "active_today": active_today,
            "new_today": new_today,
            "new_hour": new_hour,
            "events_today": events_today,
            "open_positions": open_positions,
            "pending_deposits": pending_deposits,
        }
    except Exception:
        return {}


# Ensure table exists on import
ensure_activity_table()
