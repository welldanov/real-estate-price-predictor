from pathlib import Path

from real_estate_price_predictor.database.connection import get_connection


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = PROJECT_ROOT / "sql" / "schema.sql"


def init_database() -> None:
    schema = SCHEMA_PATH.read_text(encoding="utf-8")

    with get_connection() as connection:
        connection.executescript(schema)

    print("Database initialized successfully.")


if __name__ == "__main__":
    init_database()