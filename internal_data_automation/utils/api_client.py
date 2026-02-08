import requests
import time
import logging
from typing import Dict, Any, Optional

def fetch_with_retries(url: str, params: Dict[str, Any], config: Dict[str, Any], logger: logging.Logger) -> requests.Response:
    """
    Fetches data from a URL with retries and exponential backoff.
    
    Args:
        url: The URL to fetch.
        params: Query parameters.
        config: Configuration dictionary containing api settings.
        logger: Logger instance.
        
    Returns:
        requests.Response: The successful response object.
        
    Raises:
        requests.RequestException: If all retries fail.
    """
    api_config = config.get("api", {})
    timeout = api_config.get("timeout_seconds", 10)
    max_retries = api_config.get("max_retries", 3)
    backoff_base = api_config.get("backoff_base_seconds", 1)
    
    attempt = 0
    while attempt <= max_retries:
        try:
            response = requests.get(url, params=params, timeout=timeout)
            
            # Raise for 4xx and 5xx errors, but handle 429 specifically
            response.raise_for_status()
            
            return response
            
        except requests.exceptions.RequestException as e:
            status_code = None
            if hasattr(e, 'response') and e.response is not None:
                status_code = e.response.status_code
            
            # Don't retry on 4xx errors (except 429)
            if status_code and 400 <= status_code < 500 and status_code != 429:
                logger.error(f"Client error ({status_code}) fetching {url}: {e}")
                raise e
            
            attempt += 1
            if attempt > max_retries:
                logger.error(f"Max retries ({max_retries}) exceeded for {url}. Last error: {e}")
                raise e
            
            sleep_time = backoff_base * (2 ** (attempt - 1))
            logger.warning(f"Attempt {attempt}/{max_retries} failed for {url}. Retrying in {sleep_time}s. Error: {e}")
            time.sleep(sleep_time)
            
    # Should be unreachable due to raise in loop, but for safety
    raise requests.exceptions.RequestException(f"Failed to fetch {url} after {max_retries} retries")
