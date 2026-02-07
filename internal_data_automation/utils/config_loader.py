import yaml
from pathlib import Path
from typing import Dict, Any

def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """
    Loads configuration from a YAML file.
    
    Args:
        config_path: Path to the YAML configuration file.
        
    Returns:
        Dictionary containing configuration parameters.
        
    Raises:
        FileNotFoundError: If cache file not found.
        yaml.YAMLError: If error parsing YAML file.
    """
    path = Path(config_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Config file not found at: {path.absolute()}")
        
    try:
        with open(path, 'r') as f:
            config = yaml.safe_load(f)
            return config or {}
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Error parsing config file: {e}")
