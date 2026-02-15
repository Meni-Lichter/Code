# All code in this file is related to configuration management for the application

from typing import List
import json
import os


def load_config(config_path='config.json'):
    """
    Load configuration from JSON file, or create default if not exists
    Input: config_path: Path to config JSON file (default: 'config.json')
    Output: Dictionary containing configuration settings
    """
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    else:
        # Create default config
        default_config = {
            'cbom_room_col_start': 'G',
            'cbom_room_num_row': 5,
            'cbom_room_desc_row': 4,
            'cbom_12nc_col': 'C',
            'cbom_12nc_desc_col': 'D',
            'cbom_12nc_row_start': 9
        }
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=4)
        print(f"Created default config file: {config_path}")
        return default_config
    
def save_config(config: dict, config_path: str = "config.json") -> None:
    """Save the configuration file with proper formatting."""
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print(f"Configuration saved to {config_path}")

def update_relevant_rooms(rooms: List[str], config_path: str = "config.json") -> None:
    """
    Update the relevant_rooms list in the config file.
    
    Args:
        rooms: List of room codes (e.g., ['FIT4404', 'FIT4405'])
        config_path: Path to the config file
    """
    config = load_config(config_path)
    
    # Remove duplicates and sort
    unique_rooms = sorted(set(rooms))
    
    config["relevant_rooms"]["rooms"] = unique_rooms
    
    save_config(config, config_path)
    print(f"Updated relevant_rooms with {len(unique_rooms)} rooms")

