# Weather ETL Pipeline with Apache Airflow

A complete ETL (Extract, Transform, Load) pipeline built with Apache Airflow that extracts real-time weather data from the Open-Meteo API and loads it into a PostgreSQL database.

## 🌟 Features

- **Extract**: Fetches current weather data from Open-Meteo API for London
- **Transform**: Processes and structures the raw weather data
- **Load**: Stores transformed data in PostgreSQL database
- **Automation**: Runs daily using Apache Airflow scheduling
- **Containerized**: Uses Docker for easy deployment and scalability

## 🏗️ Architecture

```
Open-Meteo API → Airflow DAG → PostgreSQL Database
     ↓              ↓              ↓
  Weather Data → Transform → Structured Storage
```

## 📋 Prerequisites

- **Docker Desktop** (for Windows/Mac) or Docker Engine (for Linux)
- **Astro CLI** - [Installation Guide](https://docs.astronomer.io/astro/cli/install-cli)
- **Python 3.8+**
- **Git**

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/etl-weather-pipeline.git
cd etl-weather-pipeline
```

### 2. Start PostgreSQL Database

```bash
docker-compose up -d
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
AIRFLOW_CONN_POSTGRES_DEFAULT=postgresql://postgres:20p@host.docker.internal:5432/postgres
AIRFLOW_CONN_OPEN_METEO_API=https://api.open-meteo.com
```

### 4. Start Airflow Development Environment

```bash
astro dev start
```

### 5. Access Airflow UI

Open your browser and navigate to: `http://localhost:8080`

**Default Credentials:**
- Username: `admin`
- Password: `admin`

## 📁 Project Structure

```
etl-weather-pipeline/
├── dags/
│   └── etl_weather.py          # Main DAG file
├── docker-compose.yml          # PostgreSQL configuration
├── Dockerfile                  # Airflow custom image
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables
├── packages.txt               # System packages (if needed)
└── README.md                  # This file
```

## 🔧 Configuration

### Database Connection

The pipeline uses PostgreSQL with the following default settings:

- **Host**: `host.docker.internal`
- **Port**: `5432`
- **Username**: `postgres`
- **Password**: `20p`
- **Database**: `postgres`

### API Configuration

Weather data is fetched from Open-Meteo API:
- **Base URL**: `https://api.open-meteo.com`
- **Location**: London (Latitude: 51.5074, Longitude: -0.1278)
- **Data**: Current weather conditions

## 📊 Data Schema

The pipeline creates a `weather_data` table with the following structure:

| Column        | Type      | Description                    |
|---------------|-----------|--------------------------------|
| latitude      | FLOAT     | Location latitude              |
| longitude     | FLOAT     | Location longitude             |
| temperature   | FLOAT     | Temperature in Celsius         |
| windspeed     | FLOAT     | Wind speed in km/h             |
| winddirection | FLOAT     | Wind direction in degrees      |
| weathercode   | INT       | Weather condition code         |
| timestamp     | TIMESTAMP | Record insertion time          |

## 🔄 DAG Details

### Schedule
- **Frequency**: Daily (`@daily`)
- **Start Date**: Yesterday's date
- **Catchup**: Disabled

### Tasks
1. **extract_weather_data**: Fetches data from Open-Meteo API
2. **transform_weather_data**: Processes and structures the data
3. **load_weather_data**: Inserts data into PostgreSQL

### Task Dependencies
```
extract_weather_data → transform_weather_data → load_weather_data
```

## 🛠️ Troubleshooting

### Common Issues

1. **Port 5432 already in use**
   ```bash
   docker-compose down
   astro dev start
   ```

2. **Connection refused to PostgreSQL**
   - Ensure PostgreSQL container is running: `docker ps`
   - Check connection settings in Airflow UI

3. **DAG not appearing in Airflow**
   - Check DAG syntax: `astro dev parse`
   - Review Airflow logs: `astro dev logs`

### Viewing Logs

```bash
# View all logs
astro dev logs

# View specific service logs
astro dev logs scheduler
astro dev logs webserver
```

## 📈 Monitoring

### Airflow UI Features
- **DAG Status**: Monitor pipeline execution
- **Task Logs**: Debug individual tasks
- **Data Lineage**: Visualize data flow
- **Metrics**: Track success rates and performance

### Database Verification

Connect to PostgreSQL to verify data:

```bash
# Connect to database
docker exec -it postgres_db psql -U postgres -d postgres

# Check data
SELECT * FROM weather_data ORDER BY timestamp DESC LIMIT 10;
```

## 🔧 Customization

### Change Location

Edit the coordinates in `dags/etl_weather.py`:

```python
LATITUDE = 'YOUR_LATITUDE'
LONGITUDE = 'YOUR_LONGITUDE'
```

### Modify Schedule

Update the schedule in the DAG definition:

```python
schedule='@hourly'  # or '@weekly', '0 */6 * * *', etc.
```

### Add More Data Fields

Extend the API call and transformation logic to include additional weather parameters like humidity, pressure, etc.

## 📦 Dependencies

### Python Packages
- `apache-airflow-providers-http`
- `apache-airflow-providers-postgres`
- `requests`

### System Requirements
- Docker Desktop 4.0+
- 4GB RAM (minimum)
- 10GB free disk space

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Open-Meteo](https://open-meteo.com/) for providing free weather API
- [Apache Airflow](https://airflow.apache.org/) community
- [Astronomer](https://www.astronomer.io/) for the Astro CLI

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/yourusername/etl-weather-pipeline/issues) page
2. Create a new issue with detailed description
3. Join the discussion in [Discussions](https://github.com/yourusername/etl-weather-pipeline/discussions)

---

**Built with ❤️ using Apache Airflow and Docker**
