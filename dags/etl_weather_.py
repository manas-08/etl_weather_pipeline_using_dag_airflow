from airflow import DAG
from airflow.providers.http.hooks.http import HttpHook
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.decorators import task
from datetime import datetime, timedelta, timezone
import requests
import json
import logging
import pytz
from typing import Dict, List, Any

# Configuration
POSTGRES_CONN_ID = 'postgres_default'
API_CONN_ID = 'open_meteo_api'

# Default locations - can be overridden from database
DEFAULT_LOCATIONS = {
    'london': {
        'name': 'London',
        'country': 'United Kingdom',
        'lat': 51.5074,
        'lon': -0.1278,
        'timezone': 'Europe/London'
    },
    'new_york': {
        'name': 'New York',
        'country': 'United States',
        'lat': 40.7128,
        'lon': -74.0060,
        'timezone': 'America/New_York'
    },
    'tokyo': {
        'name': 'Tokyo',
        'country': 'Japan',
        'lat': 35.6762,
        'lon': 139.6503,
        'timezone': 'Asia/Tokyo'
    },
    'sydney': {
        'name': 'Sydney',
        'country': 'Australia',
        'lat': -33.8688,
        'lon': 151.2093,
        'timezone': 'Australia/Sydney'
    },
    'paris': {
        'name': 'Paris',
        'country': 'France',
        'lat': 48.8566,
        'lon': 2.3522,
        'timezone': 'Europe/Paris'
    }
}

# UTC Timezone utility functions
def get_utc_now() -> datetime:
    """Return current UTC timestamp with timezone info"""
    return datetime.now(timezone.utc)

def get_local_now() -> datetime:
    """Return current local timestamp (for backward compatibility)"""
    return datetime.now()

def convert_to_utc(dt: datetime) -> datetime:
    """Convert datetime to UTC timezone-aware datetime"""
    if dt.tzinfo is None:
        # Assume local time and convert to UTC
        local_tz = pytz.timezone('Asia/Kolkata')  # Adjust for your timezone
        localized_dt = local_tz.localize(dt)
        return localized_dt.astimezone(timezone.utc)
    return dt.astimezone(timezone.utc)

default_args = {
    'owner': 'data_team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5)
}

with DAG(
    dag_id='enhanced_weather_etl_pipeline',
    default_args=default_args,
    description='Enhanced multi-location weather ETL pipeline with UTC support',
    schedule='@hourly',  # Run every hour for better data granularity
    catchup=False,
    max_active_runs=1,
    tags=['weather', 'etl', 'multi-location', 'utc']
) as dag:

    @task
    def get_active_locations() -> Dict[str, Dict]:
        """
        Get active locations from database, fallback to default locations
        """
        try:
            pg_hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
            
            query = """
            SELECT city_name, country, latitude, longitude, timezone 
            FROM cities_config 
            WHERE is_active = TRUE
            """
            
            records = pg_hook.get_records(query)
            
            if records:
                locations = {}
                for record in records:
                    city_key = record[0].lower().replace(' ', '_')
                    locations[city_key] = {
                        'name': record[0],
                        'country': record[1],
                        'lat': float(record[2]),
                        'lon': float(record[3]),
                        'timezone': record[4]
                    }
                logging.info(f"Retrieved {len(locations)} active locations from database")
                return locations
            else:
                logging.warning("No active locations found in database, using defaults")
                return DEFAULT_LOCATIONS
                
        except Exception as e:
            logging.error(f"Error fetching locations from database: {e}")
            logging.info("Falling back to default locations")
            return DEFAULT_LOCATIONS

    @task
    def extract_weather_data(locations: Dict[str, Dict]) -> Dict[str, Dict]:
        """
        Extract enhanced weather data for all locations
        """
        weather_data = {}
        
        for city_key, location in locations.items():
            try:
                # Build comprehensive API endpoint
                endpoint = (
                    f"/v1/forecast"
                    f"?latitude={location['lat']}"
                    f"&longitude={location['lon']}"
                    f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,"
                    f"is_day,precipitation,rain,showers,snowfall,weather_code,"
                    f"cloud_cover,pressure_msl,surface_pressure,wind_speed_10m,"
                    f"wind_direction_10m,wind_gusts_10m"
                    f"&daily=sunrise,sunset,uv_index_max"
                    f"&timezone={location['timezone']}"
                    f"&forecast_days=1"
                )
                
                # Make API request
                http_hook = HttpHook(http_conn_id=API_CONN_ID, method='GET')
                response = http_hook.run(endpoint)
                
                if response.status_code == 200:
                    api_data = response.json()
                    
                    # Extract current weather
                    current = api_data.get('current', {})
                    daily = api_data.get('daily', {})
                    
                    weather_data[city_key] = {
                        'location': location,
                        'current': current,
                        'daily': daily,
                        'api_response': api_data
                    }
                    
                    logging.info(f"Successfully extracted weather data for {location['name']}")
                    
                else:
                    logging.error(f"API request failed for {location['name']}: {response.status_code}")
                    
            except Exception as e:
                logging.error(f"Error extracting weather data for {location['name']}: {e}")
                
        return weather_data

    @task
    def transform_weather_data(raw_weather_data: Dict[str, Dict]) -> List[Dict]:
        """
        Transform raw weather data into structured format with UTC timestamps
        """
        transformed_records = []
        
        # Get current timestamps (both local and UTC)
        current_local = get_local_now()
        current_utc = get_utc_now()
        
        for city_key, data in raw_weather_data.items():
            try:
                location = data['location']
                current = data['current']
                daily = data['daily']
                
                # Weather code to description mapping (simplified)
                weather_codes = {
                    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
                    45: "Fog", 48: "Depositing rime fog", 51: "Light drizzle", 53: "Moderate drizzle",
                    55: "Dense drizzle", 56: "Light freezing drizzle", 57: "Dense freezing drizzle",
                    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain", 66: "Light freezing rain",
                    67: "Heavy freezing rain", 71: "Slight snow fall", 73: "Moderate snow fall",
                    75: "Heavy snow fall", 77: "Snow grains", 80: "Slight rain showers",
                    81: "Moderate rain showers", 82: "Violent rain showers", 85: "Slight snow showers",
                    86: "Heavy snow showers", 95: "Thunderstorm", 96: "Thunderstorm with slight hail",
                    99: "Thunderstorm with heavy hail"
                }
                
                weather_code = current.get('weather_code', 0)
                
                # Parse sunrise and sunset times - FIXED VERSION
                sunrise_time = None
                sunset_time = None
                if daily.get('sunrise') and len(daily['sunrise']) > 0:
                    sunrise_dt = datetime.fromisoformat(daily['sunrise'][0].replace('Z', '+00:00'))
                    sunrise_time = sunrise_dt.time().strftime('%H:%M:%S')  # Convert to string
                if daily.get('sunset') and len(daily['sunset']) > 0:
                    sunset_dt = datetime.fromisoformat(daily['sunset'][0].replace('Z', '+00:00'))
                    sunset_time = sunset_dt.time().strftime('%H:%M:%S')    # Convert to string
                
                # Parse timestamp properly - try to use API timestamp, fallback to current time
                api_timestamp = current.get('time')
                if api_timestamp:
                    try:
                        if 'T' in api_timestamp:
                            parsed_timestamp = datetime.fromisoformat(api_timestamp.replace('Z', '+00:00'))
                            if parsed_timestamp.tzinfo:
                                # Convert timezone-aware timestamp to both local and UTC
                                local_timestamp = parsed_timestamp.astimezone().replace(tzinfo=None)  # Local without timezone
                                utc_timestamp = parsed_timestamp.astimezone(timezone.utc)  # UTC with timezone
                            else:
                                # Naive timestamp - assume it's UTC
                                local_timestamp = parsed_timestamp
                                utc_timestamp = parsed_timestamp.replace(tzinfo=timezone.utc)
                        else:
                            local_timestamp = current_local
                            utc_timestamp = current_utc
                    except Exception as e:
                        logging.warning(f"Failed to parse API timestamp '{api_timestamp}': {e}")
                        local_timestamp = current_local
                        utc_timestamp = current_utc
                else:
                    local_timestamp = current_local
                    utc_timestamp = current_utc
                
                transformed_record = {
                    'city_name': location['name'],
                    'country': location['country'],
                    'latitude': location['lat'],
                    'longitude': location['lon'],
                    'temperature': current.get('temperature_2m'),
                    'feels_like': current.get('apparent_temperature'),
                    'humidity': current.get('relative_humidity_2m'),
                    'pressure': current.get('pressure_msl'),
                    'windspeed': current.get('wind_speed_10m'),
                    'winddirection': current.get('wind_direction_10m'),
                    'visibility': None,  # Not provided by this API
                    'uv_index': daily.get('uv_index_max', [None])[0],
                    'cloud_cover': current.get('cloud_cover'),
                    'weathercode': weather_code,
                    'weather_description': weather_codes.get(weather_code, f"Unknown ({weather_code})"),
                    'sunrise': sunrise_time,     # Now a string
                    'sunset': sunset_time,       # Now a string
                    'timezone': location['timezone'],
                    'timestamp': local_timestamp,      # Local timestamp (backward compatibility)
                    'timestamp_utc': utc_timestamp     # UTC timestamp (new column)
                }
                
                transformed_records.append(transformed_record)
                logging.info(f"Transformed weather data for {location['name']} - Local: {local_timestamp}, UTC: {utc_timestamp}")
                
            except Exception as e:
                logging.error(f"Error transforming data for {city_key}: {e}")
                
        return transformed_records

    @task
    def load_weather_data(transformed_records: List[Dict]) -> Dict[str, int]:
        """
        Load transformed weather data into PostgreSQL with both timestamp columns
        """
        if not transformed_records:
            logging.warning("No records to load")
            return {'loaded_records': 0, 'failed_records': 0}
        
        pg_hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
        
        # Updated insert query to include timestamp_utc column
        insert_query = """
        INSERT INTO weather_data (
            city_name, country, latitude, longitude, temperature, feels_like,
            humidity, pressure, windspeed, winddirection, visibility, uv_index,
            cloud_cover, weathercode, weather_description, sunrise, sunset,
            timezone, timestamp, timestamp_utc
        ) VALUES (
            %(city_name)s, %(country)s, %(latitude)s, %(longitude)s, %(temperature)s,
            %(feels_like)s, %(humidity)s, %(pressure)s, %(windspeed)s, %(winddirection)s,
            %(visibility)s, %(uv_index)s, %(cloud_cover)s, %(weathercode)s,
            %(weather_description)s, 
            CASE WHEN %(sunrise)s IS NOT NULL THEN %(sunrise)s::time ELSE NULL END,
            CASE WHEN %(sunset)s IS NOT NULL THEN %(sunset)s::time ELSE NULL END,
            %(timezone)s, %(timestamp)s, %(timestamp_utc)s
        )
        """
        
        loaded_records = 0
        failed_records = 0
        
        for record in transformed_records:
            try:
                pg_hook.run(insert_query, parameters=record)
                loaded_records += 1
                logging.info(f"Loaded weather data for {record['city_name']} - UTC: {record['timestamp_utc']}")
            except Exception as e:
                logging.error(f"Error loading data for {record['city_name']}: {e}")
                failed_records += 1
        
        result = {
            'loaded_records': loaded_records,
            'failed_records': failed_records,
            'total_records': len(transformed_records)
        }
        
        logging.info(f"Load summary: {result}")
        return result

    @task
    def generate_weather_summary(load_result: Dict[str, int]) -> Dict:
        """
        Generate summary statistics for the current ETL run using UTC timestamps
        """
        pg_hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
        
        # Get latest data summary using the view
        summary_query = """
        SELECT 
            COUNT(*) as total_cities,
            AVG(temperature) as avg_temperature,
            MIN(temperature) as min_temperature,
            MAX(temperature) as max_temperature,
            AVG(humidity) as avg_humidity,
            AVG(pressure) as avg_pressure,
            MIN(timestamp_utc) as earliest_data_utc,
            MAX(timestamp_utc) as latest_data_utc
        FROM latest_weather_by_city
        """
        
        summary_result = pg_hook.get_first(summary_query)
        
        # Get total records count from last 24 hours
        count_query = """
        SELECT COUNT(*) 
        FROM weather_data 
        WHERE timestamp_utc >= NOW() - INTERVAL '24 hours'
        """
        total_records_24h = pg_hook.get_first(count_query)[0]
        
        summary = {
            'etl_timestamp_utc': get_utc_now().isoformat(),
            'etl_timestamp_local': get_local_now().isoformat(),
            'load_result': load_result,
            'weather_summary': {
                'total_cities': summary_result[0] if summary_result[0] else 0,
                'avg_temperature': round(summary_result[1], 2) if summary_result[1] else None,
                'min_temperature': summary_result[2],
                'max_temperature': summary_result[3],
                'avg_humidity': round(summary_result[4], 2) if summary_result[4] else None,
                'avg_pressure': round(summary_result[5], 2) if summary_result[5] else None,
                'earliest_data_utc': summary_result[6].isoformat() if summary_result[6] else None,
                'latest_data_utc': summary_result[7].isoformat() if summary_result[7] else None,
                'total_records_24h': total_records_24h
            }
        }
        
        logging.info(f"Weather ETL Summary: {summary}")
        return summary

    @task
    def data_quality_check(load_result: Dict[str, int]) -> Dict:
        """
        Perform data quality checks on loaded data
        """
        pg_hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
        
        quality_checks = {}
        
        # Check 1: Ensure UTC timestamps are reasonable (not in future, not too old)
        utc_check_query = """
        SELECT 
            COUNT(*) as total_records,
            COUNT(CASE WHEN timestamp_utc > NOW() THEN 1 END) as future_records,
            COUNT(CASE WHEN timestamp_utc < NOW() - INTERVAL '7 days' THEN 1 END) as old_records
        FROM weather_data 
        WHERE timestamp_utc >= NOW() - INTERVAL '24 hours'
        """
        utc_check = pg_hook.get_first(utc_check_query)
        quality_checks['utc_timestamp_check'] = {
            'total_records': utc_check[0],
            'future_records': utc_check[1],
            'old_records': utc_check[2],
            'passed': utc_check[1] == 0  # No future records
        }
        
        # Check 2: Temperature range validation
        temp_check_query = """
        SELECT 
            MIN(temperature) as min_temp,
            MAX(temperature) as max_temp,
            COUNT(CASE WHEN temperature < -50 OR temperature > 60 THEN 1 END) as extreme_temps
        FROM weather_data 
        WHERE timestamp_utc >= NOW() - INTERVAL '1 hour'
        """
        temp_check = pg_hook.get_first(temp_check_query)
        quality_checks['temperature_check'] = {
            'min_temperature': temp_check[0],
            'max_temperature': temp_check[1],
            'extreme_temperatures': temp_check[2],
            'passed': temp_check[2] == 0  # No extreme temperatures
        }
        
        # Overall quality score
        passed_checks = sum(1 for check in quality_checks.values() if check.get('passed', False))
        total_checks = len(quality_checks)
        
        quality_summary = {
            'timestamp': get_utc_now().isoformat(),
            'checks': quality_checks,
            'overall_score': f"{passed_checks}/{total_checks}",
            'all_passed': passed_checks == total_checks
        }
        
        logging.info(f"Data Quality Summary: {quality_summary}")
        return quality_summary

    # Define task dependencies with enhanced monitoring
    locations = get_active_locations()
    raw_data = extract_weather_data(locations)
    transformed_data = transform_weather_data(raw_data)
    load_result = load_weather_data(transformed_data)
    summary = generate_weather_summary(load_result)
    quality_check = data_quality_check(load_result)
    
    # Set final dependencies
    [summary, quality_check]
    