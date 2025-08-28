# Unified Ads Campaign Insights Prototype

A Python prototype for consolidating and analyzing ad campaign data across multiple platforms (Google Ads, Meta, LinkedIn, TikTok).

## Features

- **Multi-platform Data Integration**: Normalizes data from different ad platforms into a unified schema
- **Core KPIs**: Calculates ROAS, CPA, and CTR with cross-platform comparisons
- **Anomaly Detection**: Uses rolling z-score (median + MAD) to detect spending and performance anomalies
- **Interactive Dashboard**: Streamlit-based UI for data visualization and insights
- **REST API**: FastAPI backend for programmatic access to metrics and insights

## Architecture

```
Mock Data Sources → Data Ingestion → Normalization → KPI Calculation → Dashboard/API
```

## Quick Start

### Option 1: Docker (Recommended)

**Prerequisites:**
- Docker and Docker Compose installed

**Run with Docker:**
```bash
# Clone and navigate to project
cd /path/to/right-programmers

# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

**Access the application:**
- **Dashboard**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/health

**Stop services:**
```bash
docker-compose down
```

**Docker Architecture:**
- **Two services**: `api` (FastAPI backend) and `dashboard` (Streamlit frontend)
- **Networking**: Internal bridge network for secure service communication
- **Health checks**: Automatic monitoring and restart capabilities
- **Volume mounts**: Live code editing with `./src` and data persistence with `./data`
- **Port mapping**: API on 8000, Dashboard on 8501

**Development with Docker:**
```bash
# View logs from all services
docker-compose logs -f

# View logs from specific service
docker-compose logs -f api
docker-compose logs -f dashboard

# Rebuild after code changes
docker-compose up --build

# Access container shell for debugging
docker exec -it ad-insights-api bash
docker exec -it ad-insights-dashboard bash
```

**Production Deployment:**
```bash
# Run in production mode (detached)
docker-compose up -d --build

# Scale services (if needed)
docker-compose up -d --scale dashboard=2

# Update services
docker-compose pull
docker-compose up -d --build
```

### Option 2: Local Development

## Setup

1. Install dependencies:
```bash
conda create -n ads_env python=3.11 #or use pyenv, whatever you choose
conda activate ads_env
pip install -r requirements.txt
```

2. Generate mock data:
```bash
python src/data_generator.py
```

3. Start the FastAPI backend:
```bash
python src/api.py
```

4. Launch the Streamlit dashboard:
```bash
streamlit run src/dashboard.py
```

5. Access the API documentation:
Swagger UI: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc
OpenAPI JSON: http://localhost:8000/openapi.json

## Project Structure

- `src/` - Main source code
  - `data_generator.py` - Generates mock ad platform data
  - `data_processor.py` - Data normalization and KPI calculations
  - `anomaly_detector.py` - Anomaly detection using statistical methods
  - `api.py` - FastAPI backend
  - `dashboard.py` - Streamlit dashboard
- `data/` - Mock data files (CSV format)
- `docs/` - Documentation and analysis

## Core KPIs

- **ROAS** (Return on Ad Spend): Revenue ÷ Spend
- **CPA** (Cost per Acquisition): Spend ÷ Conversions  
- **CTR** (Click-through Rate): Clicks ÷ Impressions

## Smart Features

- **Anomaly Detection**: Identifies unusual spending patterns or performance drops
- **Budget Recommendations**: Suggests budget adjustments based on performance trends
- **Cross-platform Insights**: Compares performance metrics across different ad platforms

