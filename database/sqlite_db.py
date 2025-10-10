# database/sqlite_db.py
import os
import sqlite3
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from dotenv import load_dotenv

# Load the main .env file
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
logger = logging.getLogger(__name__)

# Globals
connection: Optional[sqlite3.Connection] = None
db_path: Optional[str] = None

# Collection registry - maps to SQLite tables
COLLECTIONS = {
    "USERS": "users",
    "DATASETS": "datasets",
    "PREDICTIONS": "predictions",
    "REPORTS": "reports",
    "ALERTS": "alerts",
    "LOGS": "logs",
    "SESSIONS": "sessions",
}


def init_db(app=None):
    """Initialize global SQLite database connection."""
    global connection, db_path
    
    # Get database path from environment or use default
    db_path = os.environ.get("SQLITE_DB_PATH", "healthcore.db")
    
    # Make path absolute if not already
    if not os.path.isabs(db_path):
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), db_path)
    
    try:
        connection = sqlite3.connect(db_path, check_same_thread=False)
        connection.row_factory = sqlite3.Row  # Enable column access by name
        logger.info(f"✅ SQLite database connected: {db_path}")
        
        # Create tables
        create_tables()
        
        if app:
            app.db_connection = connection
            app.db = _SQLiteCompat(connection)
            
            @app.teardown_appcontext
            def _close_db(exception=None):
                close_db()
        
        return _SQLiteCompat(connection)
        
    except Exception as e:
        logger.error(f"Failed to initialize SQLite database: {e}")
        raise


def create_tables():
    """Create tables for all collections if they don't exist."""
    cursor = connection.cursor()
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT,
            password TEXT,
            created_at TEXT,
            data TEXT
        )
    """)
    
    # Datasets table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS datasets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location_name TEXT,
            timestamp TEXT,
            created_at TEXT,
            data TEXT
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_datasets_location ON datasets(location_name, timestamp)")
    
    # Predictions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT,
            data TEXT
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_predictions_created ON predictions(created_at)")
    
    # Reports table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            reporter TEXT,
            location_name TEXT,
            lat REAL,
            lng REAL,
            symptoms TEXT,
            cases INTEGER,
            turbidity REAL,
            ph REAL,
            chlorine REAL,
            tds REAL,
            fluoride REAL,
            nitrate REAL,
            chloride REAL,
            ec REAL,
            ai_prediction TEXT,
            ai_confidence REAL,
            data TEXT
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_reports_timestamp ON reports(timestamp DESC)")
    
    # Alerts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            level TEXT,
            created_at TEXT,
            data TEXT
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_level ON alerts(level, created_at DESC)")
    
    # Logs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT,
            data TEXT
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_created ON logs(created_at)")
    
    # Sessions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE,
            created_at TEXT,
            data TEXT
        )
    """)
    
    connection.commit()
    logger.info("✅ Database tables created successfully")


class _SQLiteCollection:
    """SQLite collection that mimics MongoDB collection interface."""
    
    def __init__(self, conn: sqlite3.Connection, table_name: str):
        self.conn = conn
        self.name = table_name
    
    def insert_one(self, document: Dict[str, Any]) -> Any:
        """Insert a single document."""
        cursor = self.conn.cursor()
        
        # Helper to convert datetime objects to ISO format strings
        def serialize_value(value):
            if isinstance(value, datetime):
                return value.isoformat()
            return value
        
        # Serialize datetime objects in the document
        serialized_doc = {k: serialize_value(v) for k, v in document.items()}
        
        # Special handling for reports table with structured columns
        if self.name == "reports":
            cursor.execute("""
                INSERT INTO reports (
                    timestamp, reporter, location_name, lat, lng, symptoms,
                    cases, turbidity, ph, chlorine, tds, fluoride, nitrate,
                    chloride, ec, ai_prediction, ai_confidence, data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                serialized_doc.get('timestamp'),
                serialized_doc.get('reporter'),
                serialized_doc.get('location_name'),
                serialized_doc.get('lat'),
                serialized_doc.get('lng'),
                serialized_doc.get('symptoms'),
                serialized_doc.get('cases'),
                serialized_doc.get('turbidity'),
                serialized_doc.get('ph'),
                serialized_doc.get('chlorine'),
                serialized_doc.get('tds'),
                serialized_doc.get('fluoride'),
                serialized_doc.get('nitrate'),
                serialized_doc.get('chloride'),
                serialized_doc.get('ec'),
                serialized_doc.get('ai_prediction'),
                serialized_doc.get('ai_confidence'),
                json.dumps(serialized_doc)
            ))
        else:
            # Generic insert for other tables
            data_json = json.dumps(serialized_doc)
            
            # Extract common fields if they exist
            created_at = serialized_doc.get('created_at')
            
            if self.name == "users":
                cursor.execute(
                    "INSERT INTO users (email, name, password, created_at, data) VALUES (?, ?, ?, ?, ?)",
                    (serialized_doc.get('email'), serialized_doc.get('name'), 
                     serialized_doc.get('password'), created_at, data_json)
                )
            elif self.name == "datasets":
                cursor.execute(
                    "INSERT INTO datasets (location_name, timestamp, created_at, data) VALUES (?, ?, ?, ?)",
                    (serialized_doc.get('location_name'), serialized_doc.get('timestamp'), 
                     created_at, data_json)
                )
            else:
                # Fallback for other tables
                cursor.execute(
                    f"INSERT INTO {self.name} (created_at, data) VALUES (?, ?)",
                    (created_at, data_json)
                )
        
        self.conn.commit()
        
        # Return object with inserted_id
        class InsertResult:
            def __init__(self, id):
                self.inserted_id = id
        
        return InsertResult(cursor.lastrowid)
    
    def find_one(self, query: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Find a single document."""
        cursor = self.conn.cursor()
        
        if query and 'email' in query and self.name == "users":
            cursor.execute("SELECT * FROM users WHERE email = ?", (query['email'],))
        elif query and '_id' in query:
            cursor.execute(f"SELECT * FROM {self.name} WHERE id = ?", (query['_id'],))
        else:
            cursor.execute(f"SELECT * FROM {self.name} LIMIT 1")
        
        row = cursor.fetchone()
        if row:
            return self._row_to_dict(row)
        return None
    
    def find(self, query: Dict[str, Any] = None) -> 'SQLiteCursor':
        """Find multiple documents."""
        return SQLiteCursor(self.conn, self.name, query)
    
    def delete_one(self, query: Dict[str, Any]) -> Any:
        """Delete a single document."""
        cursor = self.conn.cursor()
        
        if '_id' in query:
            cursor.execute(f"DELETE FROM {self.name} WHERE id = ?", (query['_id'],))
        elif 'email' in query and self.name == "users":
            cursor.execute("DELETE FROM users WHERE email = ?", (query['email'],))
        
        self.conn.commit()
        
        class DeleteResult:
            def __init__(self, count):
                self.deleted_count = count
        
        return DeleteResult(cursor.rowcount)
    
    def drop(self):
        """Drop the collection (table)."""
        cursor = self.conn.cursor()
        cursor.execute(f"DELETE FROM {self.name}")
        self.conn.commit()
    
    def create_index(self, field, unique=False):
        """Create an index (stub for compatibility)."""
        # Indexes are already created in create_tables()
        pass
    
    def _row_to_dict(self, row) -> Dict[str, Any]:
        """Convert SQLite row to dictionary."""
        if self.name == "reports":
            # For reports, use structured columns
            return {
                "_id": row['id'],
                "timestamp": row['timestamp'],
                "reporter": row['reporter'],
                "location_name": row['location_name'],
                "lat": row['lat'],
                "lng": row['lng'],
                "symptoms": row['symptoms'],
                "cases": row['cases'],
                "turbidity": row['turbidity'],
                "ph": row['ph'],
                "chlorine": row['chlorine'],
                "tds": row['tds'],
                "fluoride": row['fluoride'],
                "nitrate": row['nitrate'],
                "chloride": row['chloride'],
                "ec": row['ec'],
                "ai_prediction": row['ai_prediction'],
                "ai_confidence": row['ai_confidence'],
            }
        else:
            # For other tables, parse from JSON data field
            doc = json.loads(row['data']) if row['data'] else {}
            doc['_id'] = row['id']
            return doc


class SQLiteCursor:
    """Cursor for iterating over query results."""
    
    def __init__(self, conn: sqlite3.Connection, table_name: str, query: Dict[str, Any] = None):
        self.conn = conn
        self.table_name = table_name
        self.query = query
        self._sort_field = None
        self._sort_order = None
        self._limit_value = None
    
    def sort(self, field: str, order: int = 1):
        """Sort results."""
        self._sort_field = field
        self._sort_order = "ASC" if order == 1 else "DESC"
        return self
    
    def limit(self, count: int):
        """Limit number of results."""
        self._limit_value = count
        return self
    
    def __iter__(self):
        """Execute query and return iterator."""
        cursor = self.conn.cursor()
        
        # Build query
        sql = f"SELECT * FROM {self.table_name}"
        
        # Add ORDER BY if specified
        if self._sort_field:
            sql += f" ORDER BY {self._sort_field} {self._sort_order}"
        
        # Add LIMIT if specified
        if self._limit_value:
            sql += f" LIMIT {self._limit_value}"
        
        cursor.execute(sql)
        
        # Convert rows to dictionaries
        collection = _SQLiteCollection(self.conn, self.table_name)
        for row in cursor:
            yield collection._row_to_dict(row)


class _SQLiteCompat:
    """Compatibility layer to mimic MongoDB db object."""
    
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.name = os.path.basename(db_path) if db_path else "healthcore.db"
        
        # Create collection attributes
        for key, table_name in COLLECTIONS.items():
            setattr(self, table_name, _SQLiteCollection(conn, table_name))
    
    def __getitem__(self, name: str):
        """Get collection by name."""
        return _SQLiteCollection(self.conn, name)


def get_collection(name: str):
    """Get a collection by registry key or raw name."""
    if connection is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    
    table_name = COLLECTIONS.get(name, name)
    return _SQLiteCollection(connection, table_name)


def close_db():
    """Close the database connection."""
    global connection
    if connection:
        try:
            connection.close()
            logger.info("✅ SQLite database closed.")
        except Exception as e:
            logger.error(f"Error closing SQLite database: {e}")
        finally:
            connection = None
    else:
        logger.info("SQLite connection was already None.")


# Create a global db object for compatibility
class _MongoCompatWrapper:
    def __init__(self):
        self._db = None
    
    @property
    def db(self):
        if connection:
            return _SQLiteCompat(connection)
        return None

mongo = _MongoCompatWrapper()
