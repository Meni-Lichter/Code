"""
Configuration utility functions for loading and managing application configuration.
"""

import json
from pathlib import Path
from typing import Dict, Any
import os


def load_config(config_path: str = 'config.json') -> Dict[str, Any]:
    """
    Load configuration from a JSON file.
    
    Args:
        config_path: Path to the configuration JSON file (relative to project root)
    
    Returns:
        Dictionary containing the configuration settings
    
    Raises:
        FileNotFoundError: If the configuration file doesn't exist
        json.JSONDecodeError: If the configuration file is not valid JSON
    """
    # Convert to Path object
    if isinstance(config_path, str):
        config_path = Path(config_path)
    
    # If path is relative, make it relative to project root
    if not config_path.is_absolute():
        # Get project root (assuming config_util is in src/utils/)
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / config_path
    
    # Check if file exists
    if not config_path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}\n"
            f"Please ensure 'config.json' exists in the project root directory."
        )
    
    # Load and parse JSON
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"Invalid JSON in configuration file: {config_path}\n"
            f"Error: {str(e)}",
            e.doc,
            e.pos
        )
    except Exception as e:
        raise Exception(f"Error loading configuration file: {str(e)}")


def get_config_value(config: Dict[str, Any], *keys, default=None) -> Any:
    """
    Safely retrieve nested configuration values.
    
    Args:
        config: Configuration dictionary
        *keys: Sequence of keys to traverse (e.g., 'cbom', 'columns', 'room_start')
        default: Default value to return if key path doesn't exist
    
    Returns:
        The configuration value if found, otherwise the default value
    
    Example:
        >>> config = load_config()
        >>> room_start = get_config_value(config, 'cbom', 'columns', 'room_start', default='G')
    """
    value = config
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default
    return value


def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate that the configuration contains required sections.
    
    Args:
        config: Configuration dictionary to validate
    
    Returns:
        True if configuration is valid
    
    Raises:
        ValueError: If required configuration sections are missing
    """
    required_sections = ['cbom', 'ymbd', 'fit_cvi', 'validation']
    
    missing_sections = [section for section in required_sections if section not in config]
    
    if missing_sections:
        raise ValueError(
            f"Configuration is missing required sections: {', '.join(missing_sections)}"
        )
    
    return True


def save_config(config: Dict[str, Any], config_path: str = 'config.json') -> None:
    """
    Save configuration to a JSON file.
    
    Args:
        config: Configuration dictionary to save
        config_path: Path where to save the configuration file
    """
    # Convert to Path object
    if isinstance(config_path, str):
        config_path = Path(config_path)
    
    # If path is relative, make it relative to project root
    if not config_path.is_absolute():
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / config_path
    
    # Save with pretty formatting
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
