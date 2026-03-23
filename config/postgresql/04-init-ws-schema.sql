-- Weather Station MQTT Database Schema
-- This script initializes the database for storing weather station messages

\c weather

-- Create weather_messages table
-- Stores all weather messages from MQTT broker (Ecowitt WS3802)
CREATE TABLE IF NOT EXISTS weather_messages (
    id BIGSERIAL PRIMARY KEY,
    datetime TIMESTAMP WITH TIME ZONE NOT NULL,
    temperature_outside DOUBLE PRECISION,
    wind_speed DOUBLE PRECISION,
    data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_weather_messages_datetime ON weather_messages(datetime);
CREATE INDEX IF NOT EXISTS idx_weather_messages_created_at ON weather_messages(created_at);

-- Create GIN index for JSONB data column
CREATE INDEX IF NOT EXISTS idx_weather_messages_data ON weather_messages USING GIN(data);
