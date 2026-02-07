
import json
import os
import logging
from typing import List, Dict, Any

def clean_market_data(logger: logging.Logger, date_str: str) -> List[Dict[str, Any]]:
    """
    Loads raw market data, cleans, and normalizes it.

    Args:
        logger: Logger instance.
        date_str: Date string identifying the source file.

    Returns:
        List of cleaned market data records.
    """
    input_file = os.path.join("data", "raw", f"market_{date_str}.json")
    cleaned_data: List[Dict[str, Any]] = []

    if not os.path.exists(input_file):
        logger.warning(f"Market data file not found: {input_file}")
        return cleaned_data

    try:
        logger.info(f"Cleaning market data from {input_file}...")
        with open(input_file, 'r') as f:
            raw_data = json.load(f)

        # Alpha Vantage Time Series Daily format
        time_series = raw_data.get("Time Series (Daily)", {})
        
        if not time_series:
            logger.warning(f"No 'Time Series (Daily)' found in {input_file}")
            return cleaned_data

        for date, values in time_series.items():
            try:
                record = {
                    "date": date,
                    "open": float(values.get("1. open", 0)),
                    "high": float(values.get("2. high", 0)),
                    "low": float(values.get("3. low", 0)),
                    "close": float(values.get("4. close", 0)),
                    "volume": int(values.get("5. volume", 0))
                }
                cleaned_data.append(record)
            except (ValueError, TypeError) as e:
                logger.warning(f"Skipping malformed market record for date {date}: {e}")

        logger.info(f"Successfully cleaned {len(cleaned_data)} market records.")
        return cleaned_data

    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON from {input_file}: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error cleaning market data: {e}")
        return []
