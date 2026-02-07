
import json
import os
import logging
from typing import List, Dict, Any

def clean_news_data(logger: logging.Logger, date_str: str) -> List[Dict[str, Any]]:
    """
    Loads raw news data, cleans, and normalizes it.

    Args:
        logger: Logger instance.
        date_str: Date string identifying the source file.

    Returns:
        List of cleaned news data records.
    """
    input_file = os.path.join("data", "raw", f"news_{date_str}.json")
    cleaned_data: List[Dict[str, Any]] = []

    if not os.path.exists(input_file):
        logger.warning(f"News data file not found: {input_file}")
        return cleaned_data

    try:
        logger.info(f"Cleaning news data from {input_file}...")
        with open(input_file, 'r') as f:
            raw_data = json.load(f)

        articles = raw_data.get("articles", [])
        
        if not articles:
            logger.warning(f"No articles found in {input_file}")
            return cleaned_data

        for article in articles:
            try:
                # Handle source which is a dict
                source = article.get("source", {})
                source_name = source.get("name") if isinstance(source, dict) else str(source)

                record = {
                    "published_at": article.get("publishedAt"),
                    "source": source_name,
                    "title": article.get("title"),
                    "description": article.get("description"),
                    "url": article.get("url")
                }
                
                # Basic validation: Skip if critical fields are missing
                if not record["title"] or not record["url"]:
                    continue

                cleaned_data.append(record)
            except Exception as e:
                logger.warning(f"Skipping malformed news article: {e}")

        logger.info(f"Successfully cleaned {len(cleaned_data)} news articles.")
        return cleaned_data

    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON from {input_file}: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error cleaning news data: {e}")
        return []
