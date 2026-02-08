import sys
import os

# Ensure the current directory is in the python path
sys.path.append(os.getcwd())

import argparse
import sys
import uuid
from datetime import datetime
from internal_data_automation.utils.config_loader import load_config
from internal_data_automation.utils.logger import setup_logger
from internal_data_automation.ingestion.market_api import fetch_market_data
from internal_data_automation.ingestion.news_api import fetch_news_data
from internal_data_automation.processing.market_cleaner import clean_market_data
from internal_data_automation.processing.news_cleaner import clean_news_data
from internal_data_automation.storage.database import Database
from internal_data_automation.reporting.report_generator import generate_reports
from internal_data_automation.utils.validators import validate_production_requirements

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run the Internal Data Automation Pipeline.")
    
    parser.add_argument(
        "--date", 
        type=str, 
        default=datetime.now().strftime("%Y-%m-%d"),
        help="Date for the pipeline run (YYYY-MM-DD). Defaults to today."
    )
    
    parser.add_argument(
        "--skip-ingestion", 
        action="store_true", 
        help="Skip the data ingestion stage."
    )
    
    parser.add_argument(
        "--skip-processing", 
        action="store_true", 
        help="Skip the data processing stage."
    )
    
    parser.add_argument(
        "--skip-storage", 
        action="store_true", 
        help="Skip the data storage stage."
    )
    
    parser.add_argument(
        "--skip-reporting", 
        action="store_true", 
        help="Skip the reporting stage."
    )
    
    return parser.parse_args()

def validate_date(date_str):
    """Validate that the date string matches YYYY-MM-DD format."""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def check_ingestion_success(date_str):
    """Checks if ingestion was successful by looking for output files."""
    market_file = os.path.join("data", "raw", f"market_{date_str}.json")
    news_file = os.path.join("data", "raw", f"news_{date_str}.json")
    return os.path.exists(market_file) and os.path.exists(news_file)

def main():
    args = parse_arguments()
    run_id = str(uuid.uuid4())
    started_at = datetime.now().isoformat()
    db = None
    app_mode = "development" # Default
    
    try:
        # Load configuration
        config = load_config("config.yaml")
        
        # Initialize logger
        log_level = config.get("log_level", "INFO")
        logger = setup_logger(level=log_level)
        
        logger.info("Pipeline initialized successfully")
        logger.info(f"Loaded configuration for app: {config.get('app_name')}")
        logger.info(f"Pipeline run {run_id} started")
        
        # Determine Execution Mode
        app_mode = config.get("app", {}).get("mode", "development")
        if app_mode == "production":
            logger.info("Running in PRODUCTION mode")
            validate_production_requirements(config)
            logger.info("Production validation passed")

            # Setup CloudWatch Logging in Production
            aws_config = config.get("aws", {})
            log_group = aws_config.get("cloudwatch_log_group")
            if log_group:
                # Use hostname + date for unique stream name, or uuid
                import socket
                hostname = socket.gethostname()
                log_stream_prefix = aws_config.get("cloudwatch_log_stream_prefix", "pipeline-run")
                log_stream_name = f"{log_stream_prefix}-{hostname}-{args.date}-{run_id}"
                
                from internal_data_automation.utils.logger import add_cloudwatch_handler
                add_cloudwatch_handler(logger, log_group, log_stream_name)
                logger.info(f"CloudWatch logging enabled: Group={log_group}, Stream={log_stream_name}")
        else:
            logger.info("Running in DEVELOPMENT mode")

        # Initialize Database EARLY for audit logging
        db_path = config.get("storage", {}).get("database_path", "data/internal_data.db")
        db = Database(db_path, logger)
        
        # Record Pipeline Start
        db.start_pipeline_run(run_id, args.date, app_mode, started_at)

        # Validate Date
        if not validate_date(args.date):
            error_msg = f"Invalid date format: {args.date}. Expected YYYY-MM-DD."
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        date_str = args.date
        logger.info(f"Pipeline run date: {date_str}")

        # Ingestion Stage
        skip_ingestion = args.skip_ingestion
        
        # Enforce Production Rules: Ingestion cannot be skipped
        if app_mode == "production" and skip_ingestion:
            error_msg = "Production Violation: Ingestion cannot be skipped in production mode."
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        if not skip_ingestion:
            logger.info(f"Starting ingestion for date: {date_str}")
            fetch_market_data(config, logger, date_str)
            fetch_news_data(config, logger, date_str)
            logger.info("Ingestion stage completed")
            
            # Additional Production Check: Verify Ingestion Output
            if app_mode == "production":
                if not check_ingestion_success(date_str):
                    error_msg = "Production Failure: Ingestion failed to produce expected data files."
                    logger.error(error_msg)
                    raise RuntimeError(error_msg)
        else:
            logger.info("Skipping ingestion stage.")

        # Processing Stage
        market_records = []
        news_records = []
        
        if not args.skip_processing:
            logger.info("Starting processing stage...")
            market_records = clean_market_data(logger, date_str)
            logger.info(f"Processed {len(market_records)} market records")
            news_records = clean_news_data(logger, date_str)
            logger.info(f"Processed {len(news_records)} news records")
            logger.info("Processing stage completed")
        else:
             logger.info("Skipping processing stage.")

        # Storage Stage
        if not args.skip_storage:
            logger.info("Starting storage stage...")
            # DB is already initialized
            
            # Only insert if we have records or if we didn't skip processing but got 0 records
            db.insert_market_data(market_records)
            db.insert_news_data(news_records)
            logger.info("Storage stage completed")
        else:
            logger.info("Skipping storage stage.")

        # Reporting Stage
        # Reporting Stage
        if not args.skip_reporting:
            logger.info("Starting reporting stage...")
            generated_reports = generate_reports(config, logger, date_str)
            logger.info("Reporting stage completed")
            
            # --- S3 Upload (Production Only) ---
            if app_mode == "production":
                logger.info("Starting S3 upload...")
                aws_config = config.get("aws", {})
                bucket_name = aws_config.get("s3_bucket_name")
                s3_prefix = aws_config.get("s3_prefix", "internal-data-automation")
                
                from internal_data_automation.utils.aws_utils import upload_file_to_s3
                
                for report_path in generated_reports:
                    if report_path and os.path.exists(report_path):
                        file_name = os.path.basename(report_path)
                        object_name = f"{s3_prefix}/{date_str}/{file_name}"
                        logger.info(f"Uploading {file_name} to s3://{bucket_name}/{object_name}")
                        
                        success = upload_file_to_s3(report_path, bucket_name, object_name)
                        if not success:
                            error_msg = f"Failed to upload {file_name} to S3."
                            logger.error(error_msg)
                            raise RuntimeError(error_msg)
                logger.info("S3 upload completed successfully")
        else:
            logger.info("Skipping reporting stage.")
            
        # Record Success
        finished_at = datetime.now().isoformat()
        if db:
            db.mark_pipeline_success(run_id, finished_at)
        logger.info(f"Pipeline run {run_id} marked SUCCESS")
        
    except Exception as e:
        # Check if it was a system exit from argument parsing or other
        if isinstance(e, SystemExit):
            raise
            
        error_message = str(e)
        finished_at = datetime.now().isoformat()
        
        # Log error
        if 'logger' in locals():
            logger.error(f"Pipeline run {run_id} failed: {error_message}")
        else:
            print(f"Error initializing pipeline: {e}")
            
        # Record Failure in DB
        if db:
            try:
                db.mark_pipeline_failure(run_id, finished_at, error_message)
                if 'logger' in locals():
                     logger.info(f"Pipeline run {run_id} marked FAILED")
            except Exception as db_e:
                 print(f"Failed to record pipeline failure in DB: {db_e}")

        # In Production, we hard exit on failure
        # In Development, we re-raise (which also exits, but allows traceback visibility if needed)
        sys.exit(1)

if __name__ == "__main__":
    main()
