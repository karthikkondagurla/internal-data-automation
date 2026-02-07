
import requests
import json
import os
import logging
from typing import Dict, Any

def fetch_news_data(config: Dict[str, Any], logger: logging.Logger, date_str: str) -> None:
    """
    Fetches news data from NewsAPI and saves it to a JSON file.

    Args:
        config: Configuration dictionary.
        logger: Logger instance.
        date_str: Current date string (YYYY-MM-DD).
    """
    news_config = config.get("news_api", {})
    api_key = news_config.get("api_key")
    base_url = news_config.get("base_url")
    query = news_config.get("query", "finance")
    language = news_config.get("language", "en")

    if not api_key or api_key == "YOUR_NEWS_API_KEY":
        logger.warning("NewsAPI key not configured. Skipping news data ingestion.")
        return

    params = {
        "q": query,
        "from": date_str,
        "sortBy": "publishedAt",
        "apiKey": api_key,
        "language": language
    }

    try:
        logger.info(f"Fetching news data for '{query}'...")
        response = requests.get(base_url, params=params)
        response.raise_for_status()

        data = response.json()

        if data.get("status") != "ok":
            logger.error(f"NewsAPI Error: {data.get('message', 'Unknown error')}")
            return

        # Ensure raw data directory exists
        output_dir = os.path.join("data", "raw")
        os.makedirs(output_dir, exist_ok=True)

        output_file = os.path.join(output_dir, f"news_{date_str}.json")
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=4)

        logger.info(f"News data saved to {output_file}")

    except requests.RequestException as e:
        logger.error(f"HTTP Request failed for news data: {e}")
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON response for news data: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in news data ingestion: {e}")
