-- =================================================================================
--  Database: pocket_go
--  Author: a5ur4
--  Notes:
--   • Run CREATE DATABASE and connect to it before executing this script.
--   • Example (psql): CREATE DATABASE pocket_go; \c pocket_go
--   • CREATE EXTENSION requires superuser privileges.
-- =================================================================================

-- Create the database (remove IF NOT EXISTS if unsupported)
CREATE DATABASE IF NOT EXISTS pocket_go;

-- Connect to the database before running the rest of this script:
-- \c pocket_go

-- Required extensions
CREATE EXTENSION IF NOT EXISTS "pgcrypto";  -- UUID generation
CREATE EXTENSION IF NOT EXISTS "citext";    -- Case-insensitive text
CREATE EXTENSION IF NOT EXISTS "postgis";   -- Geolocation support

-- Custom ENUM type for hotel categories
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'hotel_type') THEN
        CREATE TYPE hotel_type AS ENUM ('HOTEL', 'HOSTEL', 'POUSADA', 'APARTAMENTO', 'RESORT', 'MOTEL');
    END IF;
END$$ LANGUAGE plpgsql;

-- Function to automatically set "updated_at" timestamps
CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ----------------------------
-- Table: users
-- ----------------------------
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone CITEXT,         -- Encrypted/hashed on app side; can be NULL
    telegram_id TEXT,     -- Stored as TEXT to preserve case-sensitivity if needed
    first_location GEOGRAPHY(Point, 4326),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Partial unique indexes allow multiple NULLs
CREATE UNIQUE INDEX IF NOT EXISTS users_phone_unique ON users (phone) WHERE phone IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS users_telegram_unique ON users (telegram_id) WHERE telegram_id IS NOT NULL;

CREATE TRIGGER users_set_timestamp
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- ----------------------------
-- Table: cities
-- ----------------------------
CREATE TABLE IF NOT EXISTS cities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name CITEXT NOT NULL,
    state CITEXT NOT NULL,
    country CITEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    -- Ensure uniqueness only within same state/country (e.g., “Springfield” can exist in multiple states)
    CONSTRAINT cities_name_state_country_unique UNIQUE (name, state, country)
);

CREATE TRIGGER cities_set_timestamp
BEFORE UPDATE ON cities
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- ----------------------------
-- Table: hotels
-- ----------------------------
CREATE TABLE IF NOT EXISTS hotels (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name CITEXT NOT NULL,
    description TEXT,
    type hotel_type NOT NULL,
    address CITEXT NOT NULL,
    city_id UUID REFERENCES cities(id) ON DELETE SET NULL,
    location GEOGRAPHY(Point, 4326) NOT NULL,
    web_evaluation_score NUMERIC(3,2) CHECK (web_evaluation_score >= 1.0 AND web_evaluation_score <= 5.0),
    image_url CITEXT,
    phone CITEXT,
    email CITEXT,
    website CITEXT,
    is_promoted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE hotels ADD COLUMN IF NOT EXISTS image_url CITEXT;

-- Spatial and performance indexes
CREATE INDEX IF NOT EXISTS hotels_location_idx ON hotels USING GIST (location);
CREATE INDEX IF NOT EXISTS idx_hotels_city_id ON hotels(city_id);
CREATE INDEX IF NOT EXISTS idx_hotels_is_promoted ON hotels(is_promoted);

CREATE TRIGGER hotels_set_timestamp
BEFORE UPDATE ON hotels
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- ----------------------------
-- Table: hotel_details
-- ----------------------------
CREATE TABLE IF NOT EXISTS hotel_details (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hotel_id UUID NOT NULL REFERENCES hotels(id) ON DELETE CASCADE,
    animals_allowed BOOLEAN NOT NULL DEFAULT FALSE,
    wifi_available BOOLEAN NOT NULL DEFAULT FALSE,
    breakfast_included BOOLEAN NOT NULL DEFAULT FALSE,
    gym_available BOOLEAN NOT NULL DEFAULT FALSE,
    parking_available BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_hotel_details_hotel_id ON hotel_details(hotel_id);

CREATE TRIGGER hotel_details_set_timestamp
BEFORE UPDATE ON hotel_details
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- ----------------------------
-- Table: evaluations (user reviews)
-- ----------------------------
CREATE TABLE IF NOT EXISTS evaluations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hotel_id UUID NOT NULL REFERENCES hotels(id) ON DELETE CASCADE,
    rating NUMERIC(3,2) CHECK (rating >= 1.0 AND rating <= 5.0) NOT NULL,
    comment TEXT,
    author_id UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    -- No updated_at: reviews are typically immutable
);

CREATE INDEX IF NOT EXISTS idx_evaluations_hotel_id ON evaluations(hotel_id);

-- ----------------------------
-- Table: user_searches
-- ----------------------------
CREATE TABLE IF NOT EXISTS user_searches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    search_location GEOGRAPHY(Point, 4326) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_searches_user_id ON user_searches(user_id);
CREATE INDEX IF NOT EXISTS user_searches_location_idx ON user_searches USING GIST (search_location);

-- ----------------------------
-- Table: logs
-- ----------------------------
CREATE TABLE IF NOT EXISTS logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    action CITEXT NOT NULL,
    details JSONB,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_logs_action ON logs(action);
CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs(timestamp);

-- =================================================================================
-- Cleanup Section (uncomment to drop all created objects)
-- =================================================================================
-- DROP TABLE IF EXISTS logs, user_searches, evaluations, hotel_details, hotels, cities, users CASCADE;
-- DROP TYPE IF EXISTS hotel_type CASCADE;
-- DROP EXTENSION IF EXISTS postgis;
-- DROP EXTENSION IF EXISTS citext;
-- DROP EXTENSION IF EXISTS pgcrypto;