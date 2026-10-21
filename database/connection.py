"""Database connection management with SQLite foreign key enforcement and row factory."""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional, Union
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import DB_PATH
from utils.logging_config import get_logger

logger = get_logger("database.connection")


def get_connection(db_path: Optional[Union[str, Path]] = None) -> sqlite3.Connection:
    """Create and configure a new SQLite connection.
    
    Ensures:
    - Foreign keys are explicitly enabled (`PRAGMA foreign_keys = ON`)
    - Row factory provides dictionary-like column access
    - Timeout configured to prevent lock collisions
    """
    path = str(db_path or DB_PATH)
    conn = sqlite3.connect(path, timeout=15.0)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def get_db_cursor(db_path: Optional[Union[str, Path]] = None) -> Generator[sqlite3.Cursor, None, None]:
    """Context manager for executing transactional database operations.
    
    Automatically commits on normal completion or rolls back on exceptions.
    Ensures connection is closed properly.
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error("Transaction rolled back due to error: %s", e)
        raise
    finally:
        cursor.close()
        conn.close()
