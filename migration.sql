-- Add the new UTC timestamp column
ALTER TABLE weather_data 
ADD COLUMN IF NOT EXISTS timestamp_utc TIMESTAMPTZ DEFAULT (NOW() AT TIME ZONE 'UTC');

-- Create index for the new column
CREATE INDEX IF NOT EXISTS idx_weather_timestamp_utc ON weather_data(timestamp_utc);

-- Update existing rows (convert current timestamp to UTC)
UPDATE weather_data 
SET timestamp_utc = (timestamp AT TIME ZONE 'UTC') - INTERVAL '5 hours 30 minutes'
WHERE timestamp_utc IS NULL;

-- Update the view
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
    timestamp_utc
FROM weather_data 
ORDER BY city_name, timestamp_utc DESC;