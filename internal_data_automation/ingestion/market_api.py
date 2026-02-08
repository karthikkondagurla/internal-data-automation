
import requests
import json
import os
import logging
from typing import Dict, Any
from internal_data_automation.utils.api_client import fetch_with_retries

def fetch_market_data(config: Dict[str, Any], logger: logging.Logger, date_str: str) -> None:
    """
    Fetches daily market data from Alpha Vantage and saves it to a JSON file.

    Args:
        config: Configuration dictionary.
        logger: Logger instance.
        date_str: Current date string (YYYY-MM-DD).
    """
    alpha_config = config.get("alpha_vantage", {})
    # Get API key from environment variable
    api_key = os.environ.get("ALPHA_VANTAGE_API_KEY")
    base_url = alpha_config.get("base_url")
    symbol = alpha_config.get("symbol", "SPY")

    if not api_key:
        logger.warning("ALPHA_VANTAGE_API_KEY not found in environment. Skipping market data ingestion.")
        return
    else:
        logger.info("Alpha Vantage API key loaded from environment.")

    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "apikey": api_key
    }

    try:
        logger.info(f"Fetching market data for {symbol}...")
        response = fetch_with_retries(base_url, params, config, logger)
        
        data = response.json()

        # Check if API returned an error message or rate limit note
        if "Error Message" in data:
            logger.error(f"Alpha Vantage API Error: {data['Error Message']}")
            return
        if "Note" in data:
            logger.warning(f"Alpha Vantage API Note: {data['Note']}")

        # Ensure raw data directory exists
        output_dir = os.path.join("data", "raw")
        os.makedirs(output_dir, exist_ok=True)

        output_file = os.path.join(output_dir, f"market_{date_str}.json")
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=4)
        
        logger.info(f"Market data saved to {output_file}")

    except requests.RequestException as e:
        logger.error(f"HTTP Request failed for market data: {e}")
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON response for market data: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in market data ingestion: {e}")
