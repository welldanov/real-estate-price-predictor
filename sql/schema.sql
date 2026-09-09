CREATE TABLE IF NOT EXISTS cities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL,

    lat REAL,
    lon REAL,

    UNIQUE (name)
);


-- ============================================================
-- Property categories
-- ============================================================

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Стабильный код для Python/ML
    -- apartment, house, land, commercial
    code TEXT NOT NULL UNIQUE,

    -- Человекочитаемое название
    name TEXT NOT NULL
);


-- ============================================================
-- Real estate listings
-- ============================================================

CREATE TABLE IF NOT EXISTS listings (
    id INTEGER PRIMARY KEY,

    city_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,

    -- Основной target
    price INTEGER NOT NULL,

    -- Общая площадь
    area_m2 REAL,

    -- Квартиры / дома
    rooms INTEGER,
    floor INTEGER,
    floors_total INTEGER,

    -- Характеристики здания
    building_year INTEGER,
    wall_material TEXT,

    -- Тип внутри категории
    -- Например: secondary, new_building, individual_housing
    property_type TEXT,

    -- География
    district TEXT,
    lat REAL,
    lon REAL,
    distance_to_center_km REAL,

    -- Служебные данные
    url TEXT,
    parsed_at TEXT NOT NULL,

    FOREIGN KEY (city_id)
        REFERENCES cities(id),

    FOREIGN KEY (category_id)
        REFERENCES categories(id),

    CHECK (price > 0),

    CHECK (
        area_m2 IS NULL
        OR area_m2 > 0
    ),

    CHECK (
        rooms IS NULL
        OR rooms > 0
    ),

    CHECK (
        floor IS NULL
        OR floor > 0
    ),

    CHECK (
        floors_total IS NULL
        OR floors_total > 0
    ),

    CHECK (
        floor IS NULL
        OR floors_total IS NULL
        OR floor <= floors_total
    ),

    CHECK (
        building_year IS NULL
        OR building_year BETWEEN 1800 AND 2100
    ),

    CHECK (
        lat IS NULL
        OR lat BETWEEN -90 AND 90
    ),

    CHECK (
        lon IS NULL
        OR lon BETWEEN -180 AND 180
    ),

    CHECK (
        distance_to_center_km IS NULL
        OR distance_to_center_km >= 0
    )
);


-- ============================================================
-- Indexes
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_listings_city_id
    ON listings(city_id);

CREATE INDEX IF NOT EXISTS idx_listings_category_id
    ON listings(category_id);

CREATE INDEX IF NOT EXISTS idx_listings_city_category
    ON listings(city_id, category_id);

CREATE INDEX IF NOT EXISTS idx_listings_parsed_at
    ON listings(parsed_at);


-- ============================================================
-- Initial categories
-- ============================================================

INSERT OR IGNORE INTO categories (code, name)
VALUES
    ('apartment', 'Квартиры'),
    ('house', 'Дома'),
    ('land', 'Земельные участки'),
    ('commercial', 'Коммерческая недвижимость');