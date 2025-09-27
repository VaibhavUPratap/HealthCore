"""
Database package initializer.
Exposes db helpers so you can just `from database import init_db, get_collection`.
"""

from .db import (
    init_db,
    get_collection,
    close_db,
    create_unique_index_with_report,
    find_duplicate_values,
)
from .migration_db import create_unique_index_with_report, find_duplicate_values
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError
import os
import logging
import time