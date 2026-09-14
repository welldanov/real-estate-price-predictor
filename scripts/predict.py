import numpy as np
import pandas as pd
from catboost import CatBoostRegressor

from real_estate_price_predictor.config import MODELS_DIR

from real_estate_price_predictor.ml.features import (
    prepare_apartment_features,
    prepare_house_features,
    prepare_land_features,
)

# ============================================================
# HELPERS
# ============================================================

def ask_float(prompt: str, allow_empty: bool = False):
    while True:
        value = input(prompt).strip().replace(",", ".")

        if allow_empty and value == "":
            return np.nan

        try:
            return float(value)
        except ValueError:
            print("Введите число.")


def ask_int(prompt: str, allow_empty: bool = False):
    while True:
        value = input(prompt).strip()

        if allow_empty and value == "":
            return np.nan

        try:
            return int(value)
        except ValueError:
            print("Введите целое число.")


def ask_yes_no(prompt: str) -> int:
    while True:
        value = input(f"{prompt} [д/н]: ").strip().lower()

        if value in ("д", "да", "y", "yes", "1"):
            return 1

        if value in ("н", "нет", "n", "no", "0"):
            return 0

        print("Введите д или н.")


def format_price(value: float) -> str:
    return f"{value:,.0f} ₽".replace(",", " ")


def load_model(model_name: str) -> CatBoostRegressor:
    model_path = MODELS_DIR / f"{model_name}.cbm"

    if not model_path.exists():
        raise FileNotFoundError(
            f"Модель не найдена: {model_path}"
        )

    model = CatBoostRegressor()
    model.load_model(model_path)

    return model


# ============================================================
# APARTMENT
# ============================================================

def predict_apartment():
    print("\n" + "=" * 70)
    print("ПРОГНОЗ ЦЕНЫ КВАРТИРЫ")
    print("=" * 70)

    city_name = input(
        "Город [Альметьевск]: "
    ).strip()

    if not city_name:
        city_name = "Альметьевск"

    lat = ask_float("Широта (lat): ")
    lon = ask_float("Долгота (lon): ")

    distance = ask_float(
        "Расстояние до центра, км: "
    )

    area = ask_float(
        "Площадь, м²: "
    )

    rooms = ask_int(
        "Количество комнат (Enter, если неизвестно): ",
        allow_empty=True,
    )

    is_studio = ask_yes_no(
        "Это студия?"
    )

    floor = ask_int(
        "Этаж: "
    )

    floors_total = ask_int(
        "Всего этажей: "
    )

    data = pd.DataFrame([{
        "listing_id": -1,
        "price": 1,
        "city_name": city_name,
        "lat": lat,
        "lon": lon,
        "distance_to_center_km": distance,
        "area_m2": area,
        "rooms": rooms,
        "is_studio": is_studio,
        "floor": floor,
        "floors_total": floors_total,
    }])

    X, _ = prepare_apartment_features(data)

    model = load_model("apartment_price")

    predicted_log = model.predict(X)[0]
    predicted_price = np.expm1(predicted_log)

    print("\n" + "=" * 70)
    print("РЕЗУЛЬТАТ")
    print("=" * 70)

    print(
        f"Предсказанная цена: "
        f"{format_price(predicted_price)}"
    )

    print(
        f"Предсказанная цена за м²: "
        f"{format_price(predicted_price / area)}"
    )

    actual_price = ask_float(
        "\nЕсли известна реальная цена, "
        "введите её (Enter — пропустить): ",
        allow_empty=True,
    )

    if not np.isnan(actual_price):

        error = predicted_price - actual_price
        absolute_error = abs(error)

        percentage_error = (
            absolute_error
            / actual_price
            * 100
        )

        print("\n" + "-" * 70)
        print("СРАВНЕНИЕ С РЕАЛЬНОЙ ЦЕНОЙ")
        print("-" * 70)

        print(
            f"Реальная цена:     "
            f"{format_price(actual_price)}"
        )

        print(
            f"Прогноз модели:    "
            f"{format_price(predicted_price)}"
        )

        print(
            f"Ошибка:            "
            f"{format_price(absolute_error)}"
        )

        print(
            f"Ошибка:            "
            f"{percentage_error:.2f}%"
        )

        if error < 0:
            print(
                "Модель ЗАНИЗИЛА цену."
            )
        else:
            print(
                "Модель ЗАВЫСИЛА цену."
            )


# ============================================================
# HOUSE
# ============================================================

def predict_house():
    print("\n" + "=" * 70)
    print("ПРОГНОЗ ЦЕНЫ ДОМА")
    print("=" * 70)

    city_name = input(
        "Город [Альметьевск]: "
    ).strip()

    if not city_name:
        city_name = "Альметьевск"

    lat = ask_float("Широта (lat): ")
    lon = ask_float("Долгота (lon): ")

    distance = ask_float(
        "Расстояние до центра, км: "
    )

    house_area = ask_float(
        "Площадь дома, м²: "
    )

    land_area = ask_float(
        "Площадь участка, м²: "
    )

    data = pd.DataFrame([{
        "listing_id": -1,
        "price": 1,
        "city_name": city_name,
        "lat": lat,
        "lon": lon,
        "distance_to_center_km": distance,
        "house_area_m2": house_area,
        "land_area_m2": land_area,
    }])

    X, _ = prepare_house_features(data)

    model = load_model("house_price")

    predicted_log = model.predict(X)[0]
    predicted_price = np.expm1(predicted_log)

    print("\n" + "=" * 70)
    print("РЕЗУЛЬТАТ")
    print("=" * 70)

    print(
        f"Предсказанная цена: "
        f"{format_price(predicted_price)}"
    )

    print(
        f"Цена за м² дома: "
        f"{format_price(predicted_price / house_area)}"
    )

    actual_price = ask_float(
        "\nЕсли известна реальная цена, "
        "введите её (Enter — пропустить): ",
        allow_empty=True,
    )

    if not np.isnan(actual_price):

        error = predicted_price - actual_price
        absolute_error = abs(error)

        percentage_error = (
            absolute_error
            / actual_price
            * 100
        )

        print("\n" + "-" * 70)
        print("СРАВНЕНИЕ С РЕАЛЬНОЙ ЦЕНОЙ")
        print("-" * 70)

        print(
            f"Реальная цена:     "
            f"{format_price(actual_price)}"
        )

        print(
            f"Прогноз модели:    "
            f"{format_price(predicted_price)}"
        )

        print(
            f"Ошибка:            "
            f"{format_price(absolute_error)}"
        )

        print(
            f"Ошибка:            "
            f"{percentage_error:.2f}%"
        )

        if error < 0:
            print("Модель ЗАНИЗИЛА цену.")
        else:
            print("Модель ЗАВЫСИЛА цену.")


# ============================================================
# LAND
# ============================================================

def predict_land():
    print("\n" + "=" * 70)
    print("ПРОГНОЗ ЦЕНЫ ЗЕМЕЛЬНОГО УЧАСТКА")
    print("=" * 70)

    city_name = input(
        "Город [Альметьевск]: "
    ).strip()

    if not city_name:
        city_name = "Альметьевск"

    lat = ask_float("Широта (lat): ")
    lon = ask_float("Долгота (lon): ")

    distance = ask_float(
        "Расстояние до центра, км: "
    )

    land_area = ask_float(
        "Площадь участка, м²: "
    )

    land_type = input(
        "Тип земли (например ИЖС, СНТ, ДНП): "
    ).strip()

    data = pd.DataFrame([{
        "listing_id": -1,
        "price": 1,
        "city_name": city_name,
        "lat": lat,
        "lon": lon,
        "distance_to_center_km": distance,
        "land_area_m2": land_area,
        "land_type": land_type,
    }])

    X, _ = prepare_land_features(data)

    model = load_model("land_price")

    predicted_log = model.predict(X)[0]
    predicted_price = np.expm1(predicted_log)

    print("\n" + "=" * 70)
    print("РЕЗУЛЬТАТ")
    print("=" * 70)

    print(
        f"Предсказанная цена: "
        f"{format_price(predicted_price)}"
    )

    print(
        f"Предсказанная цена за м²: "
        f"{format_price(predicted_price / land_area)}"
    )

    actual_price = ask_float(
        "\nЕсли известна реальная цена, "
        "введите её (Enter — пропустить): ",
        allow_empty=True,
    )

    if not np.isnan(actual_price):

        error = predicted_price - actual_price
        absolute_error = abs(error)

        percentage_error = (
            absolute_error
            / actual_price
            * 100
        )

        print("\n" + "-" * 70)
        print("СРАВНЕНИЕ С РЕАЛЬНОЙ ЦЕНОЙ")
        print("-" * 70)

        print(
            f"Реальная цена:     "
            f"{format_price(actual_price)}"
        )

        print(
            f"Прогноз модели:    "
            f"{format_price(predicted_price)}"
        )

        print(
            f"Ошибка:            "
            f"{format_price(absolute_error)}"
        )

        print(
            f"Ошибка:            "
            f"{percentage_error:.2f}%"
        )

        if error < 0:
            print("Модель ЗАНИЗИЛА цену.")
        else:
            print("Модель ЗАВЫСИЛА цену.")


# ============================================================
# MAIN MENU
# ============================================================

def main():

    while True:

        print("\n")
        print("=" * 70)
        print("REAL ESTATE PRICE PREDICTOR")
        print("=" * 70)

        print("1. Квартира")
        print("2. Дом")
        print("3. Земельный участок")
        print("0. Выход")

        choice = input("\nВыберите тип объекта: ").strip()

        try:

            if choice == "1":
                predict_apartment()

            elif choice == "2":
                predict_house()

            elif choice == "3":
                predict_land()

            elif choice == "0":
                print("Выход.")
                break

            else:
                print("Неизвестный пункт меню.")

        except Exception as error:

            print("\nОШИБКА:")
            print(error)

            print(
                "\nПроверьте, что все введённые "
                "значения корректны."
            )


if __name__ == "__main__":
    main()