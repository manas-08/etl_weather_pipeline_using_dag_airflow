CREATE TABLE IF NOT EXISTS weather_data (
    id SERIAL PRIMARY KEY,
    city_name VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    temperature FLOAT,
    feels_like FLOAT,
    humidity INTEGER,
    pressure FLOAT,
    windspeed FLOAT,
    winddirection FLOAT,
    visibility FLOAT,
    uv_index FLOAT,
    cloud_cover INTEGER,
    weathercode INTEGER,
    weather_description TEXT,
    sunrise TIME,
    sunset TIME,
    timezone VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    timestamp_utc TIMESTAMPTZ DEFAULT (NOW() AT TIME ZONE 'UTC'),  
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_weather_city_timestamp ON weather_data(city_name, timestamp);
CREATE INDEX IF NOT EXISTS idx_weather_timestamp ON weather_data(timestamp);
CREATE INDEX IF NOT EXISTS idx_weather_timestamp_utc ON weather_data(timestamp_utc);  -- NEW INDEX
CREATE INDEX IF NOT EXISTS idx_weather_city ON weather_data(city_name);

-- Update the view to use UTC timestamp
CREATE OR REPLACE VIEW latest_weather_by_city AS
SELECT DISTINCT ON (city_name) 
    city_name,
    country,
    latitude,
    longitude,
    temperature,
    feels_like,
    humidity,
    pressure,
    windspeed,
    winddirection,
    visibility,
    uv_index,
    cloud_cover,
    weather_description,
    timestamp,
    timestamp_utc  -- Include both timestamps
FROM weather_data 
ORDER BY city_name, timestamp_utc DESC;  -- Order by UTC timestamp

-- ...rest of your existing init.sql remains the same...

-- Insert some sample cities configuration
CREATE TABLE IF NOT EXISTS cities_config (
    id SERIAL PRIMARY KEY,
    city_name VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    timezone VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default cities
INSERT INTO cities_config (city_name, country, latitude, longitude, timezone) VALUES
('London', 'United Kingdom', 51.5074, -0.1278, 'Europe/London'),
('New York', 'United States', 40.7128, -74.0060, 'America/New_York'),
('Tokyo', 'Japan', 35.6762, 139.6503, 'Asia/Tokyo'),
('Sydney', 'Australia', -33.8688, 151.2093, 'Australia/Sydney'),
('Paris', 'France', 48.8566, 2.3522, 'Europe/Paris')
ON CONFLICT DO NOTHING;

-- Create some utility views for analytics
CREATE OR REPLACE VIEW weather_analytics AS
SELECT 
    city_name,
    country,
    AVG(temperature) as avg_temperature,
    MIN(temperature) as min_temperature,
    MAX(temperature) as max_temperature,
    AVG(humidity) as avg_humidity,
    AVG(pressure) as avg_pressure,
    AVG(windspeed) as avg_windspeed,
    COUNT(*) as record_count,
    MIN(timestamp) as first_record,
    MAX(timestamp) as last_record
FROM weather_data 
GROUP BY city_name, country;

-- Create a function to clean old data (optional)
CREATE OR REPLACE FUNCTION cleanup_old_weather_data(days_to_keep INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM weather_data 
    WHERE timestamp < NOW() - INTERVAL '1 day' * days_to_keep;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'Weather database initialized successfully at %', NOW();
END $$;