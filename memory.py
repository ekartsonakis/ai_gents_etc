"""
Memory module - SQLite database for user profile, preferences, and audit logging.
Security: Never stores passwords, CVV, card numbers, or OTP codes.
"""

import sqlite3
from datetime import datetime
from typing import Optional, Dict, Any, List

DB_PATH = "db.sqlite"


def get_connection() -> sqlite3.Connection:
    """Get a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database schema."""
    conn = get_connection()
    cursor = conn.cursor()

    # User profile table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT,
            afm TEXT,
            supply_number TEXT,
            address TEXT,
            meter_type TEXT DEFAULT 'single',
            day_split REAL DEFAULT 0.7,
            night_split REAL DEFAULT 0.3,
            email TEXT,
            phone TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # User preferences table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fixed_only BOOLEAN DEFAULT 0,
            max_contract_months INTEGER DEFAULT 24,
            max_exit_fee REAL DEFAULT 0,
            payment_method TEXT DEFAULT 'prepaid_card',
            ebill_only BOOLEAN DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Consumption history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS consumption_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            month TEXT,
            year INTEGER,
            total_kwh REAL,
            day_kwh REAL,
            night_kwh REAL,
            provider TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Audit log table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            action TEXT,
            provider TEXT,
            plan_name TEXT,
            amount REAL,
            receipt_id TEXT,
            details TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def save_user_profile(data: Dict[str, Any]) -> int:
    """Save or update user profile. Returns user ID."""
    conn = get_connection()
    cursor = conn.cursor()

    # Check if profile exists
    cursor.execute("SELECT id FROM user_profile LIMIT 1")
    existing = cursor.fetchone()

    now = datetime.now().isoformat()

    if existing:
        # Update existing
        cursor.execute("""
            UPDATE user_profile SET
                full_name = ?,
                afm = ?,
                supply_number = ?,
                address = ?,
                meter_type = ?,
                day_split = ?,
                night_split = ?,
                email = ?,
                phone = ?,
                updated_at = ?
            WHERE id = ?
        """, (
            data.get("full_name"),
            data.get("afm"),
            data.get("supply_number"),
            data.get("address"),
            data.get("meter_type", "single"),
            data.get("day_split", 0.7),
            data.get("night_split", 0.3),
            data.get("email"),
            data.get("phone"),
            now,
            existing["id"]
        ))
        user_id = existing["id"]
    else:
        # Insert new
        cursor.execute("""
            INSERT INTO user_profile (
                full_name, afm, supply_number, address, meter_type,
                day_split, night_split, email, phone, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("full_name"),
            data.get("afm"),
            data.get("supply_number"),
            data.get("address"),
            data.get("meter_type", "single"),
            data.get("day_split", 0.7),
            data.get("night_split", 0.3),
            data.get("email"),
            data.get("phone"),
            now,
            now
        ))
        user_id = cursor.lastrowid

    conn.commit()
    conn.close()
    return user_id


def get_user_profile() -> Optional[Dict[str, Any]]:
    """Get user profile."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM user_profile LIMIT 1")
    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)
    return None


def save_preferences(data: Dict[str, Any]) -> int:
    """Save or update preferences. Returns preference ID."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM preferences LIMIT 1")
    existing = cursor.fetchone()

    now = datetime.now().isoformat()

    if existing:
        cursor.execute("""
            UPDATE preferences SET
                fixed_only = ?,
                max_contract_months = ?,
                max_exit_fee = ?,
                payment_method = ?,
                ebill_only = ?,
                updated_at = ?
            WHERE id = ?
        """, (
            data.get("fixed_only", False),
            data.get("max_contract_months", 24),
            data.get("max_exit_fee", 0),
            data.get("payment_method", "prepaid_card"),
            data.get("ebill_only", False),
            now,
            existing["id"]
        ))
        pref_id = existing["id"]
    else:
        cursor.execute("""
            INSERT INTO preferences (
                fixed_only, max_contract_months, max_exit_fee,
                payment_method, ebill_only, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("fixed_only", False),
            data.get("max_contract_months", 24),
            data.get("max_exit_fee", 0),
            data.get("payment_method", "prepaid_card"),
            data.get("ebill_only", False),
            now,
            now
        ))
        pref_id = cursor.lastrowid

    conn.commit()
    conn.close()
    return pref_id


def get_preferences() -> Optional[Dict[str, Any]]:
    """Get user preferences."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM preferences LIMIT 1")
    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)
    return None


def log_audit(action: str, provider: str = None, plan_name: str = None,
              amount: float = None, receipt_id: str = None, details: str = None):
    """Log an audit entry."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO audit_log (date, action, provider, plan_name, amount, receipt_id, details)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(),
        action,
        provider,
        plan_name,
        amount,
        receipt_id,
        details
    ))

    conn.commit()
    conn.close()


def get_audit_log(limit: int = 50) -> List[Dict[str, Any]]:
    """Get audit log entries."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM audit_log ORDER BY created_at DESC LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def save_consumption(month: str, year: int, total_kwh: float,
                     day_kwh: float = None, night_kwh: float = None,
                     provider: str = None):
    """Save consumption data for a month."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO consumption_history (month, year, total_kwh, day_kwh, night_kwh, provider)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (month, year, total_kwh, day_kwh, night_kwh, provider))

    conn.commit()
    conn.close()


def get_consumption_history(limit: int = 12) -> List[Dict[str, Any]]:
    """Get consumption history."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM consumption_history ORDER BY year DESC, month DESC LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_average_consumption() -> Dict[str, float]:
    """Calculate average consumption from history."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            AVG(total_kwh) as avg_total,
            AVG(day_kwh) as avg_day,
            AVG(night_kwh) as avg_night
        FROM consumption_history
    """)

    row = cursor.fetchone()
    conn.close()

    if row and row["avg_total"]:
        return {
            "total": row["avg_total"],
            "day": row["avg_day"] or 0,
            "night": row["avg_night"] or 0
        }
    return {"total": 0, "day": 0, "night": 0}


# Initialize database on module import
init_db()
