# database/db.py
import os
import time
import logging
from typing import Optional
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ServerSelectionTimeoutError, PyMongoError
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Globals
client: Optional[MongoClient] = None
db = None

# Collection registry
COLLECTIONS = {
    "USERS": "users",
    "DATASETS": "datasets",
    "PREDICTIONS": "predictions",
    "REPORTS": "reports",
    "ALERTS": "alerts",
    "LOGS": "logs",
    "SESSIONS": "sessions",
}

# Retry controls
CONNECT_RETRIES = int(os.environ.get("MONGO_CONNECT_RETRIES", "3"))
CONNECT_BACKOFF_SEC = float(os.environ.get("MONGO_CONNECT_BACKOFF_SEC", "1.0"))


def ensure_indexes(database):
    """Create helpful indexes (idempotent)."""
    database[COLLECTIONS["USERS"]].create_index("email", unique=True)
    database[COLLECTIONS["DATASETS"]].create_index(
        [("location_name", ASCENDING), ("timestamp", DESCENDING)]
    )
    database[COLLECTIONS["PREDICTIONS"]].create_index("created_at")
    database[COLLECTIONS["REPORTS"]].create_index([("created_at", DESCENDING)])
    database[COLLECTIONS["ALERTS"]].create_index(
        [("level", ASCENDING), ("created_at", DESCENDING)]
    )
    # TTL cleanup
    database[COLLECTIONS["ALERTS"]].create_index(
        "created_at", expireAfterSeconds=60 * 60 * 24 * 90
    )
    database[COLLECTIONS["LOGS"]].create_index(
        "created_at", expireAfterSeconds=60 * 60 * 24 * 30
    )


def _connect_with_retries(uri: str) -> MongoClient:
    """Try connecting to MongoDB with retry & backoff."""
    last_exc = None
    for attempt in range(1, CONNECT_RETRIES + 1):
        try:
            client = MongoClient(uri, serverSelectionTimeoutMS=5000)
            client.admin.command("ping")
            logger.info("✅ MongoDB connection established (attempt %d)", attempt)
            return client
        except (ServerSelectionTimeoutError, PyMongoError) as e:
            last_exc = e
            logger.warning("MongoDB connect failed (attempt %d/%d): %s",
                           attempt, CONNECT_RETRIES, e)
            time.sleep(CONNECT_BACKOFF_SEC * attempt)
    logger.error("All MongoDB connection attempts failed after %d tries", CONNECT_RETRIES)
    raise last_exc


def init_db(app=None):
    """Initialize global MongoDB client and DB. Attach to Flask app if provided."""
    global client, db
    uri = os.environ.get("MONGO_URI")
    if not uri:
        raise RuntimeError("MONGO_URI environment variable is missing")

    client = _connect_with_retries(uri)

    dbname = os.environ.get("MONGO_DBNAME", "default_db")
    db = client[dbname]

    ensure_indexes(db)

    if app:
        app.mongo_client = client
        app.db = db

        @app.teardown_appcontext
        def _close_db(exception=None):
            close_db()

    return db


def get_collection(name: str):
    """Get a collection by registry key or raw name."""
    if db is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    if name in COLLECTIONS:
        return db[COLLECTIONS[name]]
    return db[name]


def close_db():
    global client
    if client:
        try:
            client.close()
            logger.info("✅ MongoDB client closed.")
        except Exception as e:
            logger.error("Error closing MongoDB client: %s", e)
        finally:
            client = None
    else:
        logger.info("MongoDB client was already None.")
    global db
    db = None