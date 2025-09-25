CREATE DATABASE pocket_go;

-- Habilitar extensões necessárias
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "citext";
CREATE EXTENSION IF NOT EXISTS "postgis"; -- Essencial para geolocalização

-- Cria um tipo personalizado para categorias de hotéis
CREATE TYPE hotel_type AS ENUM ('hotel', 'hostel', 'pousada', 'apartamento', 'resort', 'motel');

-- Função para atualizar o campo updated_at automaticamente
CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Tabela de Cidades (corrigido o id)
CREATE TABLE cities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name CITEXT NOT NULL UNIQUE,
    state CITEXT NOT NULL,
    country CITEXT NOT NULL DEFAULT 'Brasil',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Trigger para a tabela 'cities'
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON cities
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Tabela de Hotéis (com geolocalização e referências corrigidas)
CREATE TABLE hotels (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name CITEXT NOT NULL,
    description TEXT,
    type hotel_type NOT NULL,
    address CITEXT NOT NULL,
    -- Chave estrangeira correta para o ID da cidade
    city_id UUID REFERENCES cities(id) ON DELETE SET NULL,
    -- Coluna de geolocalização com PostGIS (latitude, longitude)
    location GEOGRAPHY(Point, 4326) NOT NULL,
    phone CITEXT,
    email CITEXT,
    website CITEXT,
    is_promoted BOOLEAN NOT NULL DEFAULT FALSE, -- Para o modelo de negócio
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
-- Cria um índice espacial para buscas de localização super rápidas
CREATE INDEX hotels_location_idx ON hotels USING GIST (location);

-- Trigger para a tabela 'hotels'
CREATE TRIGGER set_timestamp
BEFORE UPDATE ON hotels
FOR EACH ROW
EXECUTE FUNCTION trigger_set_timestamp();

-- Tabela de Avaliações (com tipo de dado corrigido para a nota)
CREATE TABLE evaluations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hotel_id UUID NOT NULL REFERENCES hotels(id) ON DELETE CASCADE,
    -- NUMERIC é mais preciso que FLOAT para notas
    rating NUMERIC(2, 1) CHECK (rating >= 1.0 AND rating <= 5.0) NOT NULL,
    comment TEXT,
    author_name CITEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    -- Não precisa de updated_at, pois avaliações geralmente não são editadas
);

-- Tabela para registrar as buscas dos usuários (antiga 'requests')
CREATE TABLE user_searches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_identifier CITEXT, -- Pode ser um ID do Telegram/WhatsApp
    search_location GEOGRAPHY(Point, 4326) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Tabela de Logs (sem alterações, está boa)
CREATE TABLE logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    action CITEXT NOT NULL,
    entity CITEXT NOT NULL,
    entity_id UUID,
    details JSONB, -- JSONB é mais flexível para armazenar detalhes do log
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);