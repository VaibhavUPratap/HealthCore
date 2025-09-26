# database/db.py
import os
import logging
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ServerSelectionTimeoutError, OperationFailure
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

client = None
db = None

COLLECTIONS = {
    "USERS": "users",
    "DATASETS": "datasets",
    "PREDICTIONS": "predictions",
    "REPORTS": "reports",
    "ALERTS": "alerts",
    "LOGS": "logs",
    "SESSIONS": "sessions",
}

def _safe_create_index(collection, *args, **kwargs):
    try:
        collection.create_index(*args, **kwargs)
        logger.debug("Index created on %s args=%s kwargs=%s", collection.name, args, kwargs)
    except OperationFailure as e:
        logger.error("Index creation failed on %s: %s", collection.name, e)
    except Exception as e:
        logger.exception("Unexpected error creating index on %s: %s", collection.name, e)

def ensure_indexes(database):
    skip = os.environ.get("SKIP_INDEX_CREATION", "false").lower() in ("1", "true", "yes")
    if skip:
        logger.info("Skipping index creation due to SKIP_INDEX_CREATION")
        return

    # Users: unique email
    _safe_create_index(database[COLLECTIONS["USERS"]], "email", unique=True)

    # Datasets: location + timestamp
    _safe_create_index(database[COLLECTIONS["DATASETS"]],
                       [("location_name", ASCENDING), ("timestamp", DESCENDING)])

    # Predictions
    _safe_create_index(database[COLLECTIONS["PREDICTIONS"]], "created_at")

    # Reports
    _safe_create_index(database[COLLECTIONS["REPORTS"]], [("created_at", DESCENDING)])

    # Alerts
    _safe_create_index(database[COLLECTIONS["ALERTS"]],
                       [("level", ASCENDING), ("created_at", DESCENDING)])
    # Alerts TTL — requires created_at to be a Date
    try:
        _safe_create_index(database[COLLECTIONS["ALERTS"]], "created_at", expireAfterSeconds=60 * 60 * 24 * 90)
    except Exception as e:
        logger.warning("TTL index for alerts not created: %s", e)

    # Logs TTL
    _safe_create_index(database[COLLECTIONS["LOGS"]], "created_at", expireAfterSeconds=60 * 60 * 24 * 30)


def init_db(app=None):
    global client, db
    uri = os.environ.get("MONGO_URI")
    if not uri:
        raise RuntimeError("MONGO_URI environment variable is missing")

    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        logger.info("MongoDB connection established")
    except ServerSelectionTimeoutError as e:
        logger.error("Could not connect to MongoDB: %s", e)
        raise

    dbname = os.environ.get("MONGO_DBNAME")
    if not dbname:
        # be explicit in non-dev environments
        if os.environ.get("FLASK_ENV") == "production":
            raise RuntimeError("MONGO_DBNAME must be set in production")
        dbname = "default_db"

    db = client[dbname]

    ensure_indexes(db)

    if app:
        app.mongo_client = client
        app.db = db
        # register a teardown to close the client on app shutdown (Flask example)
        try:
            @app.teardown_appcontext
            def _close_db(exception=None):
                close_db()
        except Exception:
            # if app isn't Flask or doesn't support teardown_appcontext, ignore
            pass

    return db

def get_collection(name: str):
    if name in COLLECTIONS:
        return db[COLLECTIONS[name]]
    return db[name]

def close_db():
    global client
    if client:
        client.close()
        logger.info("MongoDB client closed")
        client = None
# fallback for ad-hoc collections
# Initialize immediately if module is imported directly


if __name__ == "__main__":
    init_db()  # for standalone scripts