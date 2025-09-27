# database/migration_db.py
import logging
from .db import init_db, get_collection

# setup basic logging so you see output in console
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def find_duplicate_values(collection, field):
    """Find duplicate values for a given field in a collection."""
    pipeline = [
        {"$group": {"_id": f"${field}", "count": {"$sum": 1}}},
        {"$match": {"count": {"$gt": 1}}},
    ]
    return list(collection.aggregate(pipeline))


def create_unique_index_with_report(collection, field):
    """Report duplicates before creating a unique index."""
    dups = find_duplicate_values(collection, field)
    if dups:
        logger.warning("⚠️ Duplicates found for field '%s': %s", field, dups)
        return False
    collection.create_index(field, unique=True)
    logger.info("✅ Unique index created on '%s.%s'", collection.name, field)
    return True


if __name__ == "__main__":
    # Manual run for migrations
    db = init_db()
    users = get_collection("USERS")

    # Example: ensure "email" is unique in users
    success = create_unique_index_with_report(users, "email")
    if not success:
        logger.error("❌ Migration failed: resolve duplicates before retrying.")
