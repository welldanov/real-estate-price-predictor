from real_estate_price_predictor.ml.predictor import (
    RealEstatePredictor,
)


def main() -> None:
    predictor = RealEstatePredictor()

    price = predictor.predict_apartment(
        city_name="Альметьевск",
        lat=54.901,
        lon=52.315,
        distance_to_center_km=2.1,
        area_m2=65,
        rooms=2,
        is_studio=0,
        floor=5,
        floors_total=10,
    )

    print()
    print("=" * 50)
    print("APARTMENT PRICE PREDICTION")
    print("=" * 50)
    print(f"Predicted price: {price:,.0f} RUB")
    print("=" * 50)


if __name__ == "__main__":
    main()
