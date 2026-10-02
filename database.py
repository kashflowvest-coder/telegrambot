import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from config import DB_PATH, DEFAULT_PAPER_BALANCE, DEFAULT_TRADING_MODE, DEFAULT_EXCHANGE, DEFAULT_RISK_PERCENT


def get_connection():
    """Get a database connection with row factory enabled."""
    conn = sqlite3.connect(DB_PATH, timeout=20.0)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database tables and indexes."""
    with get_connection() as conn:
        cursor = conn.cursor()

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                trading_mode TEXT DEFAULT 'paper',
                exchange TEXT DEFAULT 'binance',
                api_key TEXT DEFAULT '',
                api_secret TEXT DEFAULT '',
                paper_balance REAL DEFAULT 10000.0,
                risk_percent REAL DEFAULT 2.0,
                is_auto_trading INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Positions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,  -- 'BUY' (LONG) or 'SELL' (SHORT)
                entry_price REAL NOT NULL,
                amount REAL NOT NULL,
                cost REAL NOT NULL,
                take_profit REAL,
                stop_loss REAL,
                trailing_stop REAL DEFAULT 0,
                highest_price REAL,
                lowest_price REAL,
                status TEXT DEFAULT 'OPEN', -- 'OPEN', 'CLOSED_TP', 'CLOSED_SL', 'CLOSED_MANUAL'
                exit_price REAL,
                pnl REAL DEFAULT 0,
                pnl_percent REAL DEFAULT 0,
                mode TEXT DEFAULT 'paper', -- 'paper' or 'live'
                opened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                closed_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)

        # AI Signals history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                action TEXT NOT NULL, -- 'STRONG BUY', 'BUY', 'NEUTRAL', 'SELL', 'STRONG SELL'
                price REAL NOT NULL,
                target_tp1 REAL,
                target_tp2 REAL,
                stop_loss REAL,
                confidence REAL,
                indicators_json TEXT,
                analysis_text TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Trade activity logs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trade_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                symbol TEXT,
                action TEXT,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Crypto deposit wallets table (Admin managed)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS crypto_wallets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                network TEXT UNIQUE NOT NULL,
                address TEXT NOT NULL,
                memo TEXT DEFAULT '',
                is_active INTEGER DEFAULT 1,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Deposits table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS deposits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                network TEXT NOT NULL,
                amount REAL NOT NULL,
                txid TEXT NOT NULL,
                status TEXT DEFAULT 'PENDING',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reviewed_at TIMESTAMP
            )
        """)

        # Withdrawals table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS withdrawals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                network TEXT NOT NULL,
                amount REAL NOT NULL,
                address TEXT NOT NULL,
                status TEXT DEFAULT 'PENDING',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reviewed_at TIMESTAMP
            )
        """)

        # Safe schema migration for users table
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN is_verified INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass

        try:
            cursor.execute("ALTER TABLE users ADD COLUMN verification_otp TEXT")
        except sqlite3.OperationalError:
            pass

        try:
            cursor.execute("ALTER TABLE users ADD COLUMN otp_created_at TIMESTAMP")
        except sqlite3.OperationalError:
            pass

        try:
            cursor.execute("ALTER TABLE users ADD COLUMN language TEXT DEFAULT 'en'")
        except sqlite3.OperationalError:
            pass

        # Populate sample wallets if empty
        cursor.execute("SELECT COUNT(*) AS count FROM crypto_wallets")
        if cursor.fetchone()["count"] == 0:
            sample_wallets = [
                ("USDT_TRC20", "TVYanSUjhVLwEd9jLt1dWY2nZWFrwEjF88", ""),
                ("USDT_BEP20", "0xDemoAddressBEP20PleaseChangeInAdmin", ""),
                ("BTC", "1QBTRUbrxySqYErsPkJdfXCL2rKWZqbvfm", ""),
                ("SOL", "DemoSolanaAddressPleaseChangeInAdmin", "")
            ]
            cursor.executemany(
                "INSERT INTO crypto_wallets (network, address, memo) VALUES (?, ?, ?)",
                sample_wallets
            )

        conn.commit()


def get_or_create_user(user_id: int, username: str = "", first_name: str = "") -> Dict[str, Any]:
    """Retrieve existing user or register a new user."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()

        if row:
            cursor.execute(
                "UPDATE users SET last_active = CURRENT_TIMESTAMP, username = ?, first_name = ? WHERE user_id = ?",
                (username or row["username"], first_name or row["first_name"], user_id)
            )
            conn.commit()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            return dict(cursor.fetchone())
        else:
            cursor.execute("""
                INSERT INTO users (user_id, username, first_name, trading_mode, exchange, paper_balance, risk_percent, language)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'en')
            """, (
                user_id, username, first_name, DEFAULT_TRADING_MODE, DEFAULT_EXCHANGE,
                DEFAULT_PAPER_BALANCE, DEFAULT_RISK_PERCENT
            ))
            conn.commit()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            return dict(cursor.fetchone())


def get_user(user_id: int) -> Optional[Dict[str, Any]]:
    """Fetch user by Telegram ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_user_language(user_id: int) -> str:
    """Fetch user's preferred interface language ('en' or 'pl')."""
    user = get_user(user_id)
    if user and user.get("language"):
        return user["language"]
    return "en"


def set_user_language(user_id: int, language: str) -> bool:
    """Update user's preferred interface language."""
    lang = "pl" if language.lower().startswith("pl") else "en"
    return update_user_settings(user_id, language=lang)


def update_user_settings(user_id: int, **kwargs) -> bool:
    """Update user fields."""
    if not kwargs:
        return False
    keys = list(kwargs.keys())
    values = list(kwargs.values())
    set_clause = ", ".join([f"{k} = ?" for k in keys])
    values.append(user_id)

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE users SET {set_clause} WHERE user_id = ?", values)
        conn.commit()
        return cursor.rowcount > 0


def create_position(
    user_id: int,
    symbol: str,
    side: str,
    entry_price: float,
    amount: float,
    cost: float,
    take_profit: Optional[float] = None,
    stop_loss: Optional[float] = None,
    mode: str = "paper",
    trailing_stop: float = 0.0
) -> int:
    """Record a newly opened trade position."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO positions (
                user_id, symbol, side, entry_price, amount, cost,
                take_profit, stop_loss, trailing_stop, highest_price, lowest_price,
                status, mode, opened_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'OPEN', ?, CURRENT_TIMESTAMP)
        """, (
            user_id, symbol, side.upper(), entry_price, amount, cost,
            take_profit, stop_loss, trailing_stop, entry_price, entry_price, mode
        ))
        pos_id = cursor.lastrowid

        # Deduct balance if paper trading
        if mode == "paper":
            cursor.execute(
                "UPDATE users SET paper_balance = paper_balance - ? WHERE user_id = ?",
                (cost, user_id)
            )

        conn.commit()
        return pos_id


def get_open_positions(user_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """Retrieve all open positions for a user, or all users if user_id is None."""
    with get_connection() as conn:
        cursor = conn.cursor()
        if user_id is not None:
            cursor.execute("SELECT * FROM positions WHERE user_id = ? AND status = 'OPEN' ORDER BY opened_at DESC", (user_id,))
        else:
            cursor.execute("SELECT * FROM positions WHERE status = 'OPEN' ORDER BY opened_at DESC")
        return [dict(row) for row in cursor.fetchall()]


def get_position(position_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve a single position by ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM positions WHERE id = ?", (position_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def update_position_extremes(position_id: int, current_price: float):
    """Update highest/lowest recorded prices for trailing stops."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE positions SET
                highest_price = MAX(COALESCE(highest_price, entry_price), ?),
                lowest_price = MIN(COALESCE(lowest_price, entry_price), ?)
            WHERE id = ?
        """, (current_price, current_price, position_id))
        conn.commit()


def close_position_in_db(
    position_id: int,
    exit_price: float,
    pnl: float,
    pnl_percent: float,
    status: str = "CLOSED_MANUAL"
) -> bool:
    """Close an open position and credit user balance if paper."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM positions WHERE id = ?", (position_id,))
        pos = cursor.fetchone()
        if not pos or pos["status"] != "OPEN":
            return False

        cursor.execute("""
            UPDATE positions SET
                status = ?,
                exit_price = ?,
                pnl = ?,
                pnl_percent = ?,
                closed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (status, exit_price, pnl, pnl_percent, position_id))

        # Return cost + pnl back to paper balance
        if pos["mode"] == "paper":
            returned_amount = pos["cost"] + pnl
            cursor.execute(
                "UPDATE users SET paper_balance = paper_balance + ? WHERE user_id = ?",
                (returned_amount, pos["user_id"])
            )

        conn.commit()
        return True


def save_signal(
    symbol: str,
    timeframe: str,
    action: str,
    price: float,
    target_tp1: Optional[float],
    target_tp2: Optional[float],
    stop_loss: Optional[float],
    confidence: float,
    indicators_dict: dict,
    analysis_text: str
) -> int:
    """Save an AI signal to history."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO signals (
                symbol, timeframe, action, price, target_tp1, target_tp2,
                stop_loss, confidence, indicators_json, analysis_text, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            symbol, timeframe, action, price, target_tp1, target_tp2,
            stop_loss, confidence, json.dumps(indicators_dict), analysis_text
        ))
        conn.commit()
        return cursor.lastrowid


def get_recent_signals(symbol: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
    """Retrieve recent AI signals."""
    with get_connection() as conn:
        cursor = conn.cursor()
        if symbol:
            cursor.execute(
                "SELECT * FROM signals WHERE symbol = ? ORDER BY timestamp DESC LIMIT ?",
                (symbol, limit)
            )
        else:
            cursor.execute("SELECT * FROM signals ORDER BY timestamp DESC LIMIT ?", (limit,))
        return [dict(row) for row in cursor.fetchall()]


def log_trade_action(user_id: int, symbol: str, action: str, details: str):
    """Log trading action for audit and user history."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO trade_logs (user_id, symbol, action, details)
            VALUES (?, ?, ?, ?)
        """, (user_id, symbol, action, details))
        conn.commit()


def get_portfolio_stats(user_id: int) -> Dict[str, Any]:
    """Calculate aggregate performance metrics for a user."""
    with get_connection() as conn:
        cursor = conn.cursor()
        user = get_user(user_id)
        if not user:
            return {}

        cursor.execute("SELECT * FROM positions WHERE user_id = ?", (user_id,))
        all_positions = [dict(r) for r in cursor.fetchall()]

        open_positions = [p for p in all_positions if p["status"] == "OPEN"]
        closed_positions = [p for p in all_positions if p["status"] != "OPEN"]

        total_closed = len(closed_positions)
        winning_trades = [p for p in closed_positions if p["pnl"] > 0]
        losing_trades = [p for p in closed_positions if p["pnl"] < 0]

        win_rate = (len(winning_trades) / total_closed * 100) if total_closed > 0 else 0.0
        total_realized_pnl = sum(p["pnl"] for p in closed_positions)
        total_open_cost = sum(p["cost"] for p in open_positions)

        return {
            "trading_mode": user["trading_mode"],
            "paper_balance": user["paper_balance"],
            "open_positions_count": len(open_positions),
            "closed_trades_count": total_closed,
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "win_rate": round(win_rate, 1),
            "total_realized_pnl": round(total_realized_pnl, 2),
            "total_open_cost": round(total_open_cost, 2),
            "is_auto_trading": bool(user["is_auto_trading"])
        }


def get_admin_stats() -> Dict[str, Any]:
    """Get global platform statistics for administrators."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS total_users FROM users")
        total_users = cursor.fetchone()["total_users"]

        cursor.execute("SELECT COUNT(*) AS total_trades FROM positions")
        total_trades = cursor.fetchone()["total_trades"]

        cursor.execute("SELECT COUNT(*) AS open_trades FROM positions WHERE status = 'OPEN'")
        open_trades = cursor.fetchone()["open_trades"]

        cursor.execute("SELECT COUNT(*) AS total_signals FROM signals")
        total_signals = cursor.fetchone()["total_signals"]

        return {
            "total_users": total_users,
            "total_trades": total_trades,
            "open_trades": open_trades,
            "total_signals": total_signals
        }


def get_all_users() -> List[Dict[str, Any]]:
    """Retrieve all registered users for admin dashboard."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
        return [dict(r) for r in cursor.fetchall()]


# ==============================================================================
# CRYPTO WALLET ADDRESS MANAGEMENT (ADMIN)
# ==============================================================================

def set_crypto_wallet(network: str, address: str, memo: str = "") -> bool:
    """Add or update a platform deposit wallet address."""
    network = network.strip().upper()
    address = address.strip()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO crypto_wallets (network, address, memo, is_active, updated_at)
            VALUES (?, ?, ?, 1, CURRENT_TIMESTAMP)
            ON CONFLICT(network) DO UPDATE SET
                address = excluded.address,
                memo = excluded.memo,
                is_active = 1,
                updated_at = CURRENT_TIMESTAMP
        """, (network, address, memo))
        conn.commit()
        return True


def get_crypto_wallets(active_only: bool = True) -> List[Dict[str, Any]]:
    """Fetch platform deposit addresses."""
    with get_connection() as conn:
        cursor = conn.cursor()
        if active_only:
            cursor.execute("SELECT * FROM crypto_wallets WHERE is_active = 1 ORDER BY network ASC")
        else:
            cursor.execute("SELECT * FROM crypto_wallets ORDER BY network ASC")
        return [dict(r) for r in cursor.fetchall()]


def get_crypto_wallet(network: str) -> Optional[Dict[str, Any]]:
    """Fetch wallet details for a specific network."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM crypto_wallets WHERE network = ?", (network.upper(),))
        row = cursor.fetchone()
        return dict(row) if row else None


# ==============================================================================
# DEPOSITS MANAGEMENT
# ==============================================================================

def create_deposit_request(user_id: int, network: str, amount: float, txid: str) -> int:
    """Submit a deposit transaction for admin review."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO deposits (user_id, network, amount, txid, status, created_at)
            VALUES (?, ?, ?, ?, 'PENDING', CURRENT_TIMESTAMP)
        """, (user_id, network.upper(), float(amount), txid.strip()))
        conn.commit()
        return cursor.lastrowid


def get_deposit_request(deposit_id: int) -> Optional[Dict[str, Any]]:
    """Fetch deposit by ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM deposits WHERE id = ?", (deposit_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_pending_deposits() -> List[Dict[str, Any]]:
    """Fetch all pending deposits awaiting admin approval."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT d.*, u.username, u.first_name
            FROM deposits d
            LEFT JOIN users u ON d.user_id = u.user_id
            WHERE d.status = 'PENDING'
            ORDER BY d.created_at DESC
        """)
        return [dict(r) for r in cursor.fetchall()]


def update_deposit_status(deposit_id: int, status: str) -> bool:
    """Approve or reject a deposit. If approved, credit user paper balance."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM deposits WHERE id = ?", (deposit_id,))
        dep = cursor.fetchone()
        if not dep or dep["status"] != "PENDING":
            return False

        cursor.execute("""
            UPDATE deposits SET status = ?, reviewed_at = CURRENT_TIMESTAMP WHERE id = ?
        """, (status.upper(), deposit_id))

        if status.upper() == "APPROVED":
            # Credit user's balance
            cursor.execute("""
                UPDATE users SET paper_balance = paper_balance + ? WHERE user_id = ?
            """, (dep["amount"], dep["user_id"]))

        conn.commit()
        return True


# ==============================================================================
# OTP USER VERIFICATION
# ==============================================================================

def generate_user_otp(user_id: int) -> str:
    """Generate a secure 6-digit OTP code for user verification."""
    import random
    otp = f"{random.randint(100000, 999999)}"
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users SET verification_otp = ?, otp_created_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        """, (otp, user_id))
        conn.commit()
    return otp


def verify_user_otp(user_id: int, otp_input: str) -> bool:
    """Verify submitted 6-digit OTP and activate user account."""
    otp_input = otp_input.strip()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT verification_otp FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if row and row["verification_otp"] == otp_input:
            cursor.execute("""
                UPDATE users SET is_verified = 1, verification_otp = NULL WHERE user_id = ?
            """, (user_id,))
            conn.commit()
            return True
    return False


def is_user_verified(user_id: int) -> bool:
    """Check if user account is verified."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT is_verified FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        return bool(row["is_verified"]) if row else False


def admin_verify_user(user_id: int, status: int = 1) -> bool:
    """Admin bypass to manually verify or revoke a user."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET is_verified = ? WHERE user_id = ?", (status, user_id))
        conn.commit()
        return cursor.rowcount > 0


def verify_user(user_id: int) -> bool:
    """Instantly activate and verify user account."""
    return admin_verify_user(user_id, 1)


# ==============================================================================
# WITHDRAWALS
# ==============================================================================

def create_withdrawal_request(user_id: int, network: str, amount: float, address: str) -> Optional[int]:
    """Submit a withdrawal request. Deducts balance if sufficient."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT paper_balance FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if not row or row["paper_balance"] < amount:
            return None

        # Deduct balance
        cursor.execute("UPDATE users SET paper_balance = paper_balance - ? WHERE user_id = ?", (amount, user_id))
        cursor.execute("""
            INSERT INTO withdrawals (user_id, network, amount, address, status, created_at)
            VALUES (?, ?, ?, ?, 'PENDING', CURRENT_TIMESTAMP)
        """, (user_id, network.upper(), float(amount), address.strip()))
        conn.commit()
        return cursor.lastrowid


def get_user_withdrawals(user_id: int) -> List[Dict[str, Any]]:
    """Retrieve withdrawal history for a user."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM withdrawals WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
        return [dict(r) for r in cursor.fetchall()]


def get_pending_withdrawals() -> List[Dict[str, Any]]:
    """Retrieve all pending withdrawals."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT w.*, u.username, u.first_name
            FROM withdrawals w
            LEFT JOIN users u ON w.user_id = u.user_id
            WHERE w.status = 'PENDING'
            ORDER BY w.created_at DESC
        """)
        return [dict(r) for r in cursor.fetchall()]


def update_withdrawal_status(withdrawal_id: int, status: str) -> bool:
    """Update withdrawal status to APPROVED or REJECTED. If rejected, refund balance."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM withdrawals WHERE id = ?", (withdrawal_id,))
        w = cursor.fetchone()
        if not w or w["status"] != "PENDING":
            return False

        cursor.execute("UPDATE withdrawals SET status = ?, reviewed_at = CURRENT_TIMESTAMP WHERE id = ?", (status.upper(), withdrawal_id))
        if status.upper() == "REJECTED":
            cursor.execute("UPDATE users SET paper_balance = paper_balance + ? WHERE user_id = ?", (w["amount"], w["user_id"]))
        conn.commit()
        return True


# Initialize on import
init_db()

