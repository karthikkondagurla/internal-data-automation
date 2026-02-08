# Internal Data Automation

## Overview
The **Internal Data Automation** project is a comprehensive ETL (Extract, Transform, Load) pipeline designed to ingest, process, store, and report on financial market data and related news. It automates the daily workflow of fetching data from external APIs (Alpha Vantage, NewsAPI), cleaning it for analysis, persisting it in a local database, and generating daily summaries.

## Architecture
The pipeline consists of four distinct stages:

1.  **Ingestion**: Fetches raw JSON data from external providers.
2.  **Processing**: Cleanses, normalizes, and extracts relevant fields from the raw data.
3.  **Storage**: Persists the structured data into a SQLite database.
4.  **Reporting**: Generates summary text reports and CSV exports of the collected data.

```mermaid
graph LR
    A[Alpha Vantage / NewsAPI] -->|Ingestion| B(Raw JSON)
    B -->|Processing| C(Cleaned Data)
    C -->|Storage| D[(SQLite DB)]
    D -->|Reporting| E(Reports & CSVs)
```

## Folder Structure
```text
internal-data-automation/
├── config.yaml             # Configuration and API keys
├── requirements.txt        # Python dependencies
├── run_pipeline.py         # Main entry point (CLI)
├── reports/                # Generated reports
├── logs/                   # Pipeline execution logs
├── data/
│   ├── raw/                # Raw API responses
│   └── internal_data.db    # SQLite database
└── internal_data_automation/
    ├── ingestion/          # Data fetching modules
    ├── processing/         # Data cleaning modules
    ├── storage/            # Database operations
    └── reporting/          # Report generation
```

## Setup Instructions

1.  **Prerequisites**: Python 3.8+ installed.
2.  **Clone the Repository**:
    ```bash
    git clone <repository-url>
    cd internal-data-automation
    ```
3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration
Create a `.env` file in the project root to set your API keys:

```bash
ALPHA_VANTAGE_API_KEY="your_actual_key"
NEWS_API_KEY="your_actual_key"
```

The pipeline will automatically load these environment variables. `config.yaml` handles other settings like retries and timeouts.

## Usage

The pipeline is executed via `run_pipeline.py`. It supports command-line arguments for flexibility.

### Standard Run (Daily Sync)
Runs the full pipeline for the current date.
```bash
python run_pipeline.py
```

### Run for a Specific Date
Fetches and processes data for a historical date.
```bash
python run_pipeline.py --date 2026-02-01
```

### Partial Runs
You can skip specific stages using flags:
```bash
# Skip ingestion (e.g., if re-processing existing raw data)
python run_pipeline.py --skip-ingestion

# Skip reporting (e.g., just ingesting and storing)
python run_pipeline.py --skip-reporting
```

Available flags:
- `--skip-ingestion`
- `--skip-processing`
- `--skip-storage`
- `--skip-reporting`

## Outputs
- **Logs**: `logs/pipeline.log` contains detailed execution logs.
- **Reports**: 
  - `reports/summary_{date}.txt`: Daily summary of records processed.
  - `reports/market_data_{date}.csv`: Export of market data.

## Running with Docker

You can run the pipeline in a Docker container to ensure a consistent environment.

### 1. Build the Image
```bash
docker build -t internal-data-automation .
```

### 2. Run the Container
You need to pass your API keys as environment variables. You can do this using the `--env-file` flag with your local `.env` file.

To PERSIST data (database, reports, logs), you must mount volumes:

```bash
docker run --rm \
  --env-file .env \
  -v "$(pwd)/data:/app/data" \
  -v "$(pwd)/reports:/app/reports" \
  -v "$(pwd)/logs:/app/logs" \
  internal-data-automation
```

**Note for Windows (PowerShell):**
Replace `$(pwd)` with `${PWD}`:

```powershell
docker run --rm `
  --env-file .env `
  -v "${PWD}/data:/app/data" `
  -v "${PWD}/reports:/app/reports" `
  -v "${PWD}/logs:/app/logs" `
  internal-data-automation
```

### 3. Override Command
To run with specific flags (e.g., skip ingestion):

```bash
docker run --rm --env-file .env ... internal-data-automation python run_pipeline.py --skip-ingestion
```

## Deployment
For detailed instructions on deploying this project to AWS EC2, please refer to [deployment_guide.md](deployment_guide.md).

## Future Improvements
- Add email notifications for report delivery.
- Migrate storage to PostgreSQL for scale.
- Implement dashboarding (e.g., Streamlit) on top of the database.
