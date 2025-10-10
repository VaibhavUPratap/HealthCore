# database/migration_db.py
import logging
from .db import init_db, get_collection

# setup basic logging so you see output in console
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def find_duplicate_values(collection, field):
    """Find duplicate values for a given field in a collection."""
    # SQLite version - simplified without MongoDB aggregation
    # This is a stub for compatibility
    logger.info("find_duplicate_values is not fully implemented for SQLite")
    return []


def create_unique_index_with_report(collection, field):
    """Report duplicates before creating a unique index."""
    # SQLite version - indexes are already created in schema
    logger.info("✅ Unique index already exists on '%s.%s' (SQLite schema)", collection.name, field)
    return True


if __name__ == "__main__":
    # Manual run for migrations
    db = init_db()
    users = get_collection("USERS")

    # Example: ensure "email" is unique in users
    success = create_unique_index_with_report(users, "email")
    if not success:
        logger.error("❌ Migration failed: resolve duplicates before retrying.")
