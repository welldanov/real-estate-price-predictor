import argparse
import logging
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path

from real_estate_price_predictor.database.connection import create_connection
from real_estate_price_predictor.database.repositories import (
    upsert_apartment,
    upsert_category,
    upsert_city,
    upsert_house,
    upsert_land,
    upsert_listing,
)
from real_estate_price_predictor.ingestion.models import ListingType
from real_estate_price_predictor.ingestion.normalizer import normalize
from real_estate_price_predictor.ingestion.reader import extract_records, read_json
from real_estate_price_predictor.ingestion.validator import validate_record

logger = logging.getLogger(__name__)


@dataclass
class SkippedRecord:
    listing_id: int | None
    record_number: int
    reason: str


@dataclass
class ImportResult:
    total: int = 0
    imported: int = 0
    skipped: int = 0
    skipped_records: list[SkippedRecord] = field(
        default_factory=list
    )

    def add_skip(
            self,
            listing_id: int | None,
            record_number: int,
            reason: str,
    ) -> None:
        self.skipped += 1
        self.skipped_records.append(
            SkippedRecord(
                listing_id=listing_id,
                record_number=record_number,
                reason=reason,
            )
        )


def collect_json_files(
        path: Path,
) -> list[Path]:
    if path.is_file():
        if path.suffix.lower() != ".json":
            raise ValueError(
                f"Expected JSON file: {path}"
            )

        return [path]

    if path.is_dir():
        files = sorted(path.glob("*.json"))

        if not files:
            raise ValueError(
                f"No JSON files found in: {path}"
            )

        return files

    raise FileNotFoundError(
        f"Path does not exist: {path}"
    )


def save_listing(
        conn: sqlite3.Connection,
        record,
) -> None:
    upsert_city(
        conn,
        record.city,
    )

    upsert_category(
        conn,
        record.category,
    )

    upsert_listing(
        conn,
        record.listing,
    )

    match record.listing_type:
        case ListingType.APARTMENT:
            if record.apartment is None:
                raise ValueError(
                    "Apartment data is missing"
                )

            upsert_apartment(
                conn,
                record.apartment,
            )

        case ListingType.HOUSE:
            if record.house is None:
                raise ValueError(
                    "House data is missing"
                )

            upsert_house(
                conn,
                record.house,
            )

        case ListingType.LAND:
            if record.land is None:
                raise ValueError(
                    "Land data is missing"
                )

            upsert_land(
                conn,
                record.land,
            )

        case _:
            raise ValueError(
                f"Unsupported listing type: "
                f"{record.listing_type}"
            )


def import_file(
        json_path: Path,
        db_path: Path,
) -> ImportResult:
    logger.info(
        "Importing: %s",
        json_path,
    )

    raw_data = read_json(json_path)

    records = extract_records(raw_data)

    logger.info(
        "Records found: %d",
        len(records),
    )

    result = ImportResult(
        total=len(records),
    )

    conn = create_connection(db_path)

    try:
        for index, raw_record in enumerate(records, start=1):
            listing_id = (
                raw_record.get("id")
                if isinstance(raw_record, dict)
                else None
            )

            try:
                validated_record = validate_record(
                    raw_record
                )

                normalized_record = normalize(
                    validated_record
                )

                save_listing(
                    conn,
                    normalized_record,
                )

                conn.commit()

                result.imported += 1

                logger.debug(
                    "Imported listing: %s",
                    normalized_record.listing.id,
                )

            except Exception as exc:
                conn.rollback()

                reason = type(exc).__name__

                result.add_skip(
                    listing_id=listing_id,
                    record_number=index,
                    reason=reason,
                )

                logger.warning(
                    "Skipped: id=%s, record #%d, reason=%s",
                    listing_id,
                    index,
                    reason,
                )

    finally:
        conn.close()

    logger.info(
        "Finished %s: imported=%d skipped=%d",
        json_path,
        result.imported,
        result.skipped,
    )

    return result


def import_path(
        input_path: Path,
        db_path: Path,
) -> ImportResult:
    files = collect_json_files(
        input_path
    )

    total_result = ImportResult()

    for json_file in files:
        result = import_file(
            json_path=json_file,
            db_path=db_path,
        )

        total_result.total += result.total
        total_result.imported += result.imported
        total_result.skipped += result.skipped
        total_result.skipped_records.extend(
            result.skipped_records
        )

    return total_result


def print_result(
        result: ImportResult,
) -> None:
    print()
    print("Import finished.")
    print(f"Total:    {result.total}")
    print(f"Imported: {result.imported}")
    print(f"Skipped:  {result.skipped}")

    if result.skipped_records:
        print()
        print("Skipped listings:")

        for record in result.skipped_records:
            print(
                f"  id={record.listing_id} | "
                f"record #{record.record_number} | "
                f"{record.reason}"
            )


def configure_logging(
        verbose: bool,
) -> None:
    level = (
        logging.DEBUG
        if verbose
        else logging.INFO
    )

    logging.basicConfig(
        level=level,
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(message)s"
        ),
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Import Avito JSON data into SQLite."
        )
    )

    parser.add_argument(
        "input",
        type=Path,
        help=(
            "JSON file or directory "
            "with JSON files"
        ),
    )

    parser.add_argument(
        "--db",
        type=Path,
        default=Path(
            "data/real_estate.db"
        ),
        help=(
            "SQLite database path"
        ),
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug logging",
    )

    args = parser.parse_args()

    configure_logging(
        verbose=args.verbose,
    )

    result = import_path(
        input_path=args.input,
        db_path=args.db,
    )

    print_result(result)


if __name__ == "__main__":
    main()
