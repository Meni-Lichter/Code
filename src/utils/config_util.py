"""
Configuration utility functions for loading and managing application configuration.
"""

import json
from pathlib import Path
from typing import Dict, Any, Union


def load_config(config_path: Union[str, Path] = "config/config.json") -> Dict[str, Any]:
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
            f"Please ensure 'config/config.json' exists in the config directory."
        )

    # Load and parse JSON
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"Invalid JSON in configuration file: {config_path}\n" f"Error: {str(e)}", e.doc, e.pos
        )
    except Exception as e:
        raise Exception(f"Error loading configuration file: {str(e)}")


def save_config(
    config: Dict[str, Any], config_path: Union[str, Path] = "config/config.json"
) -> None:
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
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def get_last_files(config_path: Union[str, Path] = "config/config.json") -> Dict[str, str]:
    """Get last used file paths from config
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Dictionary with last file paths (cbom, ymbd, fit_cvi)
    """
    config = load_config(config_path)
    return config.get("last_files", {"cbom": "", "ymbd": "", "fit_cvi": ""})


def save_last_files(
    file_paths: Dict[str, str], config_path: Union[str, Path] = "config/config.json"
) -> None:
    """Save last used file paths to config
    
    Args:
        file_paths: Dictionary with file paths (cbom, ymbd, fit_cvi)
        config_path: Path to configuration file
    """
    config = load_config(config_path)
    config["last_files"] = file_paths
    save_config(config, config_path)
