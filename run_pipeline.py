import sys
import os

# Ensure the current directory is in the python path
sys.path.append(os.getcwd())

from internal_data_automation.utils.config_loader import load_config
from internal_data_automation.utils.logger import setup_logger
from internal_data_automation.ingestion.market_api import fetch_market_data
from internal_data_automation.ingestion.news_api import fetch_news_data
from internal_data_automation.processing.market_cleaner import clean_market_data
from internal_data_automation.processing.news_cleaner import clean_news_data
from datetime import datetime

def main():
    try:
        # Load configuration
        config = load_config("config.yaml")
        
        # Initialize logger
        log_level = config.get("log_level", "INFO")
        logger = setup_logger(level=log_level)
        
        logger.info("Pipeline initialized successfully")
        logger.info(f"Loaded configuration for app: {config.get('app_name')}")

        # Ingestion Stage
        date_str = datetime.now().strftime("%Y-%m-%d")
        logger.info(f"Starting ingestion for date: {date_str}")
        
        fetch_market_data(config, logger, date_str)
        fetch_news_data(config, logger, date_str)
        
        logger.info("Ingestion stage completed")

        # Processing Stage
        logger.info("Starting processing stage...")
        
        market_records = clean_market_data(logger, date_str)
        logger.info(f"Processed {len(market_records)} market records")
        
        news_records = clean_news_data(logger, date_str)
        logger.info(f"Processed {len(news_records)} news records")
        
        logger.info("Processing stage completed")
        
    except Exception as e:
        print(f"Error initializing pipeline: {e}")
        # In case of missing dependencies like PyYAML, this will catch it
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
