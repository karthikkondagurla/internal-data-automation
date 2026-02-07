import sys
import os

# Ensure the current directory is in the python path
sys.path.append(os.getcwd())

import argparse
import sys
from datetime import datetime
from internal_data_automation.utils.config_loader import load_config
from internal_data_automation.utils.logger import setup_logger
from internal_data_automation.ingestion.market_api import fetch_market_data
from internal_data_automation.ingestion.news_api import fetch_news_data
from internal_data_automation.processing.market_cleaner import clean_market_data
from internal_data_automation.processing.news_cleaner import clean_news_data
from internal_data_automation.storage.database import Database
from internal_data_automation.reporting.report_generator import generate_reports

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

def main():
    args = parse_arguments()
    
    try:
        # Load configuration
        config = load_config("config.yaml")
        
        # Initialize logger
        log_level = config.get("log_level", "INFO")
        logger = setup_logger(level=log_level)
        
        logger.info("Pipeline initialized successfully")
        logger.info(f"Loaded configuration for app: {config.get('app_name')}")
        
        # Validate Date
        if not validate_date(args.date):
            logger.error(f"Invalid date format: {args.date}. Expected YYYY-MM-DD.")
            sys.exit(1)
            
        date_str = args.date
        logger.info(f"Pipeline run date: {date_str}")

        # Ingestion Stage
        if not args.skip_ingestion:
            logger.info(f"Starting ingestion for date: {date_str}")
            fetch_market_data(config, logger, date_str)
            fetch_news_data(config, logger, date_str)
            logger.info("Ingestion stage completed")
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
            db_path = config.get("storage", {}).get("database_path", "data/internal_data.db")
            db = Database(db_path, logger)
            
            # Only insert if we have records or if we didn't skip processing but got 0 records
            # If we skipped processing, records lists are empty, so effectively nothing happens, 
            # but we invoke the method to ensure standard flow or handles empty list check internally
            db.insert_market_data(market_records)
            db.insert_news_data(news_records)
            logger.info("Storage stage completed")
        else:
            logger.info("Skipping storage stage.")

        # Reporting Stage
        if not args.skip_reporting:
            logger.info("Starting reporting stage...")
            generate_reports(config, logger, date_str)
            logger.info("Reporting stage completed")
        else:
            logger.info("Skipping reporting stage.")
        
    except Exception as e:
        # Fallback logging if logger isn't initialized yet
        print(f"Error initializing pipeline: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
