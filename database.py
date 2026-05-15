"""
Database Layer
===============
SQLite database for users, products, interactions, reviews, and recommendations.
"""

import sqlite3
import os
import hashlib
import time
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "store.db")


@contextmanager
def get_db():
    """Context manager for database connections."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    """Create all tables if they don't exist."""
    with get_db() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            display_name TEXT,
            created_at REAL DEFAULT (strftime('%s','now'))
        );

        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            subcategory TEXT DEFAULT '',
            description TEXT DEFAULT '',
            price REAL NOT NULL,
            brand TEXT DEFAULT '',
            rating REAL DEFAULT 0.0,
            review_count INTEGER DEFAULT 0,
            tags TEXT DEFAULT '',
            image_emoji TEXT DEFAULT '📦',
            popularity_score REAL DEFAULT 0.0
        );

        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            interaction_type TEXT NOT NULL,
            timestamp REAL DEFAULT (strftime('%s','now')),
            duration REAL DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        );

        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            rating REAL NOT NULL,
            comment TEXT DEFAULT '',
            timestamp REAL DEFAULT (strftime('%s','now')),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        );

        CREATE TABLE IF NOT EXISTS recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            score REAL NOT NULL,
            method TEXT DEFAULT 'hybrid',
            generated_at REAL DEFAULT (strftime('%s','now')),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        );

        CREATE INDEX IF NOT EXISTS idx_interactions_user ON interactions(user_id);
        CREATE INDEX IF NOT EXISTS idx_interactions_product ON interactions(product_id);
        CREATE INDEX IF NOT EXISTS idx_interactions_type ON interactions(interaction_type);
        CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
        CREATE INDEX IF NOT EXISTS idx_recommendations_user ON recommendations(user_id);
        """)


# ─── User Operations ────────────────────────────────────────────

def hash_password(password):
    """Hash password with SHA-256 + salt."""
    salt = "rec_sys_salt_2025"
    return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()


def create_user(username, email, password, display_name=None):
    """Create a new user. Returns user_id or None if exists."""
    pw_hash = hash_password(password)
    display = display_name or username
    try:
        with get_db() as conn:
            cur = conn.execute(
                "INSERT INTO users (username, email, password_hash, display_name) VALUES (?, ?, ?, ?)",
                (username, email, pw_hash, display)
            )
            return cur.lastrowid
    except sqlite3.IntegrityError:
        return None


def authenticate_user(username, password):
    """Authenticate user. Returns user dict or None."""
    pw_hash = hash_password(password)
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE username = ? AND password_hash = ?",
            (username, pw_hash)
        ).fetchone()
        return dict(row) if row else None


def get_user(user_id):
    """Get user by ID."""
    with get_db() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return dict(row) if row else None


def get_all_users():
    """Get all users."""
    with get_db() as conn:
        rows = conn.execute("SELECT id, username, display_name, email, created_at FROM users").fetchall()
        return [dict(r) for r in rows]


# ─── Product Operations ─────────────────────────────────────────

def get_all_products():
    """Get all products."""
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM products ORDER BY popularity_score DESC").fetchall()
        return [dict(r) for r in rows]


def get_product(product_id):
    """Get single product."""
    with get_db() as conn:
        row = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
        return dict(row) if row else None


def get_products_by_category(category):
    """Get products in a category."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM products WHERE category = ? ORDER BY popularity_score DESC",
            (category,)
        ).fetchall()
        return [dict(r) for r in rows]


def get_categories():
    """Get all unique categories."""
    with get_db() as conn:
        rows = conn.execute("SELECT DISTINCT category FROM products ORDER BY category").fetchall()
        return [r["category"] for r in rows]


def search_products(query):
    """Search products by name, category, tags, description."""
    with get_db() as conn:
        q = f"%{query}%"
        rows = conn.execute(
            """SELECT * FROM products
            WHERE name LIKE ? OR category LIKE ? OR tags LIKE ? OR description LIKE ?
            ORDER BY popularity_score DESC LIMIT 100""",
            (q, q, q, q)
        ).fetchall()
        return [dict(r) for r in rows]


def get_product_ids():
    """Get all product IDs."""
    with get_db() as conn:
        rows = conn.execute("SELECT id FROM products").fetchall()
        return [r["id"] for r in rows]


# ─── Interaction Operations ──────────────────────────────────────

def record_interaction(user_id, product_id, interaction_type, duration=0):
    """Record a user interaction."""
    with get_db() as conn:
        conn.execute(
            "INSERT INTO interactions (user_id, product_id, interaction_type, duration) VALUES (?, ?, ?, ?)",
            (user_id, product_id, interaction_type, duration)
        )


def get_user_interactions(user_id, interaction_type=None, limit=100):
    """Get interactions for a user."""
    with get_db() as conn:
        if interaction_type:
            rows = conn.execute(
                """SELECT i.*, p.name, p.category, p.price, p.image_emoji, p.rating
                FROM interactions i JOIN products p ON i.product_id = p.id
                WHERE i.user_id = ? AND i.interaction_type = ?
                ORDER BY i.timestamp DESC LIMIT ?""",
                (user_id, interaction_type, limit)
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT i.*, p.name, p.category, p.price, p.image_emoji, p.rating
                FROM interactions i JOIN products p ON i.product_id = p.id
                WHERE i.user_id = ?
                ORDER BY i.timestamp DESC LIMIT ?""",
                (user_id, limit)
            ).fetchall()
        return [dict(r) for r in rows]


def get_all_interactions():
    """Get all interactions."""
    with get_db() as conn:
        rows = conn.execute(
            """SELECT i.*, u.username, p.name as product_name, p.category
            FROM interactions i
            JOIN users u ON i.user_id = u.id
            JOIN products p ON i.product_id = p.id
            ORDER BY i.timestamp DESC"""
        ).fetchall()
        return [dict(r) for r in rows]


def get_user_category_affinity(user_id):
    """Calculate category affinity scores for a user based on interactions."""
    with get_db() as conn:
        rows = conn.execute(
            """SELECT p.category,
                SUM(CASE interaction_type
                    WHEN 'purchase' THEN 5
                    WHEN 'like' THEN 3
                    WHEN 'wishlist' THEN 2
                    WHEN 'view' THEN 1
                    ELSE 0.5
                END) as affinity_score,
                COUNT(*) as interaction_count
            FROM interactions i
            JOIN products p ON i.product_id = p.id
            WHERE i.user_id = ?
            GROUP BY p.category
            ORDER BY affinity_score DESC""",
            (user_id,)
        ).fetchall()
        return [dict(r) for r in rows]


def get_recently_viewed(user_id, limit=10):
    """Get recently viewed products for a user."""
    with get_db() as conn:
        rows = conn.execute(
            """SELECT DISTINCT p.*, MAX(i.timestamp) as last_viewed
            FROM interactions i JOIN products p ON i.product_id = p.id
            WHERE i.user_id = ? AND i.interaction_type = 'view'
            GROUP BY p.id
            ORDER BY last_viewed DESC LIMIT ?""",
            (user_id, limit)
        ).fetchall()
        return [dict(r) for r in rows]


# ─── Review Operations ────────────────────────────────────────────

def add_review(user_id, product_id, rating, comment=""):
    """Add or update a review."""
    with get_db() as conn:
        existing = conn.execute(
            "SELECT id FROM reviews WHERE user_id = ? AND product_id = ?",
            (user_id, product_id)
        ).fetchone()
        if existing:
            conn.execute(
                "UPDATE reviews SET rating = ?, comment = ?, timestamp = strftime('%s','now') WHERE id = ?",
                (rating, comment, existing["id"])
            )
        else:
            conn.execute(
                "INSERT INTO reviews (user_id, product_id, rating, comment) VALUES (?, ?, ?, ?)",
                (user_id, product_id, rating, comment)
            )
        # Update product average rating
        avg = conn.execute(
            "SELECT AVG(rating) as avg_r, COUNT(*) as cnt FROM reviews WHERE product_id = ?",
            (product_id,)
        ).fetchone()
        conn.execute(
            "UPDATE products SET rating = ?, review_count = ? WHERE id = ?",
            (round(avg["avg_r"], 2), avg["cnt"], product_id)
        )


def get_product_reviews(product_id):
    """Get reviews for a product."""
    with get_db() as conn:
        rows = conn.execute(
            """SELECT r.*, u.username, u.display_name
            FROM reviews r JOIN users u ON r.user_id = u.id
            WHERE r.product_id = ?
            ORDER BY r.timestamp DESC""",
            (product_id,)
        ).fetchall()
        return [dict(r) for r in rows]


# ─── Analytics Queries ─────────────────────────────────────────

def get_interaction_stats():
    """Get overall interaction statistics."""
    with get_db() as conn:
        stats = {}
        stats["total_users"] = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        stats["total_products"] = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        stats["total_interactions"] = conn.execute("SELECT COUNT(*) FROM interactions").fetchone()[0]
        stats["total_reviews"] = conn.execute("SELECT COUNT(*) FROM reviews").fetchone()[0]

        rows = conn.execute(
            "SELECT interaction_type, COUNT(*) as cnt FROM interactions GROUP BY interaction_type"
        ).fetchall()
        stats["by_type"] = {r["interaction_type"]: r["cnt"] for r in rows}

        rows = conn.execute(
            """SELECT p.category, COUNT(*) as cnt
            FROM interactions i JOIN products p ON i.product_id = p.id
            GROUP BY p.category ORDER BY cnt DESC LIMIT 15"""
        ).fetchall()
        stats["by_category"] = {r["category"]: r["cnt"] for r in rows}

        return stats


def get_trending_products(limit=20):
    """Get trending products based on recent interaction volume."""
    with get_db() as conn:
        rows = conn.execute(
            """SELECT p.*,
                COUNT(i.id) as recent_interactions,
                SUM(CASE i.interaction_type
                    WHEN 'purchase' THEN 5
                    WHEN 'like' THEN 3
                    WHEN 'wishlist' THEN 2
                    WHEN 'view' THEN 1
                    ELSE 0.5
                END) as trend_score
            FROM products p
            LEFT JOIN interactions i ON p.id = i.product_id
            GROUP BY p.id
            ORDER BY trend_score DESC
            LIMIT ?""",
            (limit,)
        ).fetchall()
        return [dict(r) for r in rows]
