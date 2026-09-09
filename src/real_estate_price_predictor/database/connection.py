from pathlib import Path
import sqlite3


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATABASE_PATH = PROJECT_ROOT / "data" / "real_estate.db"


def get_connection() -> sqlite3.Connection:
    """Create and configure a SQLite database connection."""
    connection = sqlite3.connect(DATABASE_PATH)

    # SQLite по умолчанию не проверяет FOREIGN KEY.
    connection.execute("PRAGMA foreign_keys = ON")

    # Позволяет обращаться к колонкам по имени:
    # row["price"] вместо row[3]
    connection.row_factory = sqlite3.Row

    return connection