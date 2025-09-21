# 🌤️ Multi-Location Weather ETL Pipeline

A comprehensive real-time weather data pipeline that extracts weather data from Open-Meteo API for multiple cities, processes it with Apache Airflow, stores it in PostgreSQL, and visualizes it with interactive Grafana dashboards.

## 🌟 Key Features

- **Real-time Multi-City Data**: Weather monitoring for 5 major global cities
- **Advanced ETL Pipeline**: Apache Airflow orchestration with data quality checks
- **Interactive Dashboards**: Grafana with multi-city selection and time series visualization
- **UTC Timestamp Support**: Proper timezone handling across all components
- **Containerized Architecture**: Complete Docker Compose setup for easy deployment
- **Data Quality Monitoring**: Temperature validation and comprehensive ETL summaries

## 🌍 Monitored Cities

| City | Coordinates | Timezone |
|------|-------------|----------|
| **London, UK** | 51.5074°N, -0.1278°W | GMT |
| **New York, USA** | 40.7128°N, -74.0060°W | EST |
| **Tokyo, Japan** | 35.6762°N, 139.6503°E | JST |
| **Sydney, Australia** | -33.8688°S, 151.2093°E | AEST |
| **Paris, France** | 48.8566°N, 2.3522°E | CET |

## 🏗️ System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Open-Meteo    │───▶│  Apache Airflow  │───▶│   PostgreSQL    │───▶│     Grafana     │
│   Weather API   │    │   ETL Pipeline   │    │    Database     │    │   Dashboard     │
└─────────────────┘    └──────────────────┘    └─────────────────┘    └─────────────────┘
        │                        │                        │                        │
   Weather Data              Data Processing         Structured Storage      Interactive Viz
   (5 Cities)               & Quality Checks        (UTC Timestamps)        (Multi-City)
```

## 📋 Prerequisites

- Docker Desktop or Docker Engine
- Astro CLI for Airflow development
- Python 3.9+
- 4GB RAM minimum
- 10GB free disk space

## 🚀 Getting Started

### Service Access Points

| Service | URL | Default Credentials |
|---------|-----|-------------------|
| **Airflow Webserver** | http://localhost:8080 | admin / admin |
| **Grafana Dashboard** | http://localhost:3000 | admin / admin |
| **PostgreSQL Database** | localhost:5432 | postgres / postgres |

### Quick Launch

1. Clone repository and navigate to project directory
2. Start PostgreSQL and Grafana services with Docker Compose
3. Launch Airflow development environment with Astro CLI
4. Trigger the ETL pipeline manually or wait for scheduled runs
5. Access Grafana dashboard to view weather data visualizations

## 📁 Project Structure

```
etl_weather_pipeline_proj/
├── dags/
│   └── etl_weather_.py           # Multi-city ETL DAG with quality checks
├── grafana/
│   ├── provisioning/
│   │   ├── datasources/
│   │   │   └── postgres.yml      # PostgreSQL data source configuration
│   │   └── dashboards/
│   │       └── weather-dashboard.json  # Interactive multi-city dashboard
├── sql/
│   └── create_weather_table.sql  # Database schema with UTC support
├── docker-compose.yml            # PostgreSQL + Grafana services
├── Dockerfile                    # Custom Airflow container
├── requirements.txt              # Python dependencies
└── .gitignore                   # Git ignore patterns
```

## 📊 Database Schema

The `weather_data` table stores comprehensive weather information:

- **Identifiers**: Auto-increment ID, city name, coordinates
- **Weather Metrics**: Temperature (°C), humidity (%), wind speed & direction
- **Metadata**: Weather descriptions, local timestamp, UTC timestamp
- **Data Types**: Optimized for time-series analysis and geographic queries

## 🔄 ETL Pipeline Details

### DAG Configuration
- **Schedule**: Hourly execution (configurable)
- **Retries**: Automatic retry logic with exponential backoff
- **Monitoring**: Comprehensive logging and error handling
- **Data Quality**: Built-in validation and quality checks

### Pipeline Tasks

1. **Extract**: Fetch current weather data from Open-Meteo API for all cities
2. **Transform**: Process API responses, standardize formats, add UTC timestamps
3. **Load**: Insert structured data into PostgreSQL with duplicate handling
4. **Validate**: Run data quality checks and temperature range validation
5. **Summarize**: Generate ETL run summaries and success metrics

## 📈 Grafana Dashboard

### Available Visualizations

- **Temperature Time Series**: Multi-city temperature trends with interactive legend
- **Humidity Monitoring**: Real-time humidity tracking with percentage scaling
- **Current Conditions Table**: Latest weather data for all cities
- **Humidity Gauge**: Single-city humidity indicator with color-coded thresholds
- **Temperature Rankings**: Highest temperatures by city for selected time period

### Interactive Features

- **Multi-City Selection**: Filter data by specific cities or view all
- **Time Range Controls**: Configurable time windows (last 24h, 7 days, custom)
- **Auto Refresh**: 5-minute automatic dashboard updates
- **Responsive Design**: Optimized for desktop and mobile viewing

## 🔧 Technical Configuration

### Environment Setup
The system uses environment variables for database connections, API endpoints, and service credentials. All sensitive information is properly isolated using Docker environment files and Airflow connections.

### Data Quality Assurance
- Temperature range validation (-50°C to 60°C)
- Required field presence checks
- UTC timestamp consistency validation
- API response validation and error handling

### Monitoring & Alerting
- ETL pipeline success/failure tracking
- Data freshness monitoring
- API response time metrics
- Database connection health checks

## 🎯 Customization Options

### Adding Cities
Extend the location list in the DAG configuration to monitor additional cities worldwide.

### Modifying Schedule
Adjust the DAG schedule from hourly to daily, or create custom cron expressions for specific timing needs.

### Dashboard Enhancement
Add new panels, modify existing visualizations, or create additional dashboards for specific use cases.

### API Parameters
Extend weather data collection to include additional parameters like pressure, visibility, or UV index.

## 🛠️ Troubleshooting Guide

### Common Issues & Solutions

**Database Connection Problems**: Verify PostgreSQL container status and network connectivity
**Dashboard No Data Issues**: Check data existence in database and Grafana data source configuration
**DAG Execution Failures**: Review Airflow logs for API connectivity or data processing errors
**API Rate Limiting**: Monitor request frequency and implement appropriate delays if needed

### System Monitoring
Monitor service logs, database performance, and dashboard query execution times for optimal system health.

## 📦 Technology Stack

### Core Components
- **Apache Airflow 2.7+**: Workflow orchestration and scheduling
- **PostgreSQL 13**: Time-series data storage with UTC support  
- **Grafana 10+**: Interactive data visualization and dashboards
- **Docker**: Containerization and service orchestration

### Python Libraries
- Weather data processing and API integration
- Database connectivity and ORM operations
- Data validation and quality assurance
- Logging and monitoring utilities

## 🔍 Data Quality & Monitoring

### Quality Metrics
- Data completeness across all monitored cities
- Temperature value validation and outlier detection
- Timestamp consistency and UTC conversion accuracy
- API response reliability and error rates

### Performance Monitoring
- ETL pipeline execution times and success rates
- Database query performance and storage optimization
- Dashboard rendering performance and user experience
- System resource utilization and scalability metrics

## 🤝 Contributing

We welcome contributions to enhance the weather ETL pipeline. Please fork the repository, create feature branches for development, and submit pull requests with comprehensive testing.

### Development Workflow
- Fork repository and create development branches
- Test changes locally with the full stack
- Ensure data quality checks pass
- Update documentation for new features
- Submit pull requests with detailed descriptions

## 📄 License & Acknowledgments

This project is open-source under the MIT License. We acknowledge the excellent free services and tools that make this project possible:

- **Open-Meteo** for providing free weather API access
- **Apache Airflow** community for robust workflow orchestration
- **Grafana Labs** for powerful visualization capabilities
- **PostgreSQL** community for reliable database technology

## 🏆 Project Achievements

- ✅ **Production-Ready Pipeline**: Robust ETL with comprehensive error handling
- ✅ **Multi-City Monitoring**: Simultaneous weather tracking for 5 major cities
- ✅ **Interactive Visualization**: User-friendly dashboards with real-time updates
- ✅ **Data Quality Assurance**: Built-in validation and monitoring
- ✅ **Containerized Deployment**: Easy setup and scalability
- ✅ **Comprehensive Documentation**: Detailed setup and troubleshooting guides

---

*A complete weather data pipeline for real-time multi-city monitoring and analysis*