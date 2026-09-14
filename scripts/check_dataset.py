from real_estate_price_predictor.config import DB_PATH

from real_estate_price_predictor.database.connection import create_connection

from real_estate_price_predictor.ml.dataset import (
    load_apartments,
    load_houses,
    load_lands,
)


def main():
    conn = create_connection(DB_PATH)

    apartments = load_apartments(conn)
    houses = load_houses(conn)
    lands = load_lands(conn)

    print("APARTMENTS")
    print(apartments.shape)
    print(apartments.head())
    print()

    print("HOUSES")
    print(houses.shape)
    print(houses.head())
    print()

    print("LANDS")
    print(lands.shape)
    print(lands.head())


if __name__ == "__main__":
    main()
