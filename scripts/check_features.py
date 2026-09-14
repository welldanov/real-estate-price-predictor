from real_estate_price_predictor.config import DB_PATH

from real_estate_price_predictor.ml.dataset import (
    load_apartments,
    load_houses,
    load_lands,
)

from real_estate_price_predictor.ml.features import (
    prepare_apartment_features,
    prepare_house_features,
    prepare_land_features,
)


def main():
    apartments = load_apartments(DB_PATH)
    houses = load_houses(DB_PATH)
    lands = load_lands(DB_PATH)

    x_apartment, y_apartment = (
        prepare_apartment_features(apartments)
    )

    x_house, y_house = (
        prepare_house_features(houses)
    )

    x_land, y_land = (
        prepare_land_features(lands)
    )

    print("APARTMENTS")
    print("X:", x_apartment.shape)
    print("y:", y_apartment.shape)
    print(x_apartment.head())
    print()

    print("HOUSES")
    print("X:", x_house.shape)
    print("y:", y_house.shape)
    print(x_house.head())
    print()

    print("LANDS")
    print("X:", x_land.shape)
    print("y:", y_land.shape)
    print(x_land.head())


if __name__ == "__main__":
    main()
