-- CITIES

CREATE TABLE IF NOT EXISTS cities (
    id INTEGER PRIMARY KEY NOT NULL,

    name TEXT NOT NULL,

    lat REAL NOT NULL,
    lon REAL NOT NULL,

    CHECK (lat BETWEEN -90 AND 90),

    CHECK (lon BETWEEN -180 AND 180)
);


-- CATEGORIES

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY NOT NULL,

    name TEXT NOT NULL
);


-- LISTINGS

CREATE TABLE IF NOT EXISTS listings (
    id INTEGER PRIMARY KEY NOT NULL,

    city_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,

    price INTEGER NOT NULL,

    formatted_address TEXT NOT NULL,
    district TEXT,

    lat REAL NOT NULL,
    lon REAL NOT NULL,

    distance_to_center_km REAL NOT NULL,

    description TEXT NOT NULL,

    url TEXT NOT NULL,
    parsed_at TEXT NOT NULL,

    FOREIGN KEY (city_id)
        REFERENCES cities(id),

    FOREIGN KEY (category_id)
        REFERENCES categories(id),


    -- INSPECTIONS

    CHECK (price > 0),

    CHECK (lat BETWEEN -90 AND 90),

    CHECK (lon BETWEEN -180 AND 180),

    CHECK (distance_to_center_km >= 0)
);


-- APARTMENTS

CREATE TABLE IF NOT EXISTS apartments (
    listing_id INTEGER PRIMARY KEY NOT NULL,

    area_m2 REAL NOT NULL,
    rooms INTEGER,
    is_studio BOOLEAN NOT NULL,
    floor INTEGER NOT NULL,
    floors_total INTEGER NOT NULL,

    FOREIGN KEY (listing_id)
        REFERENCES listings(id)
        ON DELETE CASCADE,


    -- INSPECTIONS

    CHECK (area_m2 > 0),

    CHECK (
        rooms IS NULL
        OR rooms > 0
    ),

    CHECK (floor > 0),

    CHECK (floors_total > 0),

    CHECK (floor <= floors_total)
);


-- HOUSES

CREATE TABLE IF NOT EXISTS houses (
    listing_id INTEGER PRIMARY KEY NOT NULL,

    house_area_m2 REAL NOT NULL,
    land_area_m2 REAL NOT NULL,

    FOREIGN KEY (listing_id)
        REFERENCES listings(id)
        ON DELETE CASCADE,


    -- INSPECTIONS

    CHECK (house_area_m2 > 0),

    CHECK (land_area_m2 > 0)
);


-- LANDS

CREATE TABLE IF NOT EXISTS lands (
    listing_id INTEGER PRIMARY KEY NOT NULL,

    land_area_m2 REAL NOT NULL,
    land_type TEXT NOT NULL,

    FOREIGN KEY (listing_id)
        REFERENCES listings(id)
        ON DELETE CASCADE,


    -- INSPECTIONS

    CHECK (land_area_m2 > 0)
);


-- ============================================================

-- INDEXES

CREATE INDEX IF NOT EXISTS idx_listings_city_id
    ON listings(city_id);

CREATE INDEX IF NOT EXISTS idx_listings_category_id
    ON listings(category_id);