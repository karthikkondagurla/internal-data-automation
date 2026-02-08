import os
from typing import Dict, Any

def validate_production_requirements(config: Dict[str, Any]) -> None:
    """
    Validates that the configuration meets production requirements.
    
    Args:
        config: Configuration dictionary.
        
    Raises:
        RuntimeError: If any production requirement is missing or invalid.
    """
    app_config = config.get("app", {})
    mode = app_config.get("mode", "development")
    
    if mode != "production":
        return

    # Check Alpha Vantage API Key in ENV
    if not os.environ.get("ALPHA_VANTAGE_API_KEY"):
         raise RuntimeError("Production validation failed: ALPHA_VANTAGE_API_KEY is missing in environment.")

    # Check NewsAPI Key in ENV
    if not os.environ.get("NEWS_API_KEY"):
        raise RuntimeError("Production validation failed: NEWS_API_KEY is missing in environment.")

    # Check Database Path
    db_path = config.get("storage", {}).get("database_path")
    if not db_path:
         raise RuntimeError("Production validation failed: Database path is not configured.")

    return
