# database/db.py
# This module now uses SQLite instead of MongoDB
import os
import logging
from typing import Optional
from dotenv import load_dotenv

# Import from SQLite module
from .sqlite_db import (
    init_db as sqlite_init_db,
    get_collection as sqlite_get_collection,
    close_db as sqlite_close_db,
    COLLECTIONS,
    mongo as sqlite_mongo
)

# Load the main .env file explicitly to avoid conflicts with database/.env
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
logger = logging.getLogger(__name__)

# Globals - for compatibility
client: Optional[any] = None
db = None


def ensure_indexes(database):
    """Create helpful indexes (idempotent) - stub for SQLite compatibility."""
    # Indexes are already created in SQLite schema
    # This function is kept for compatibility
    pass


# Removed MongoDB connection logic - using SQLite now


def init_db(app=None):
    """Initialize database. Now uses SQLite instead of MongoDB."""
    global db
    logger.info("🔄 Initializing SQLite database (MongoDB alternative)")
    db = sqlite_init_db(app)
    return db


def get_collection(name: str):
    """Get a collection (table) by registry key or raw name."""
    return sqlite_get_collection(name)


def close_db():
    """Close database connection."""
    sqlite_close_db()
    global db
    db = None

# Use the SQLite mongo compatibility wrapper
mongo = sqlite_mongo