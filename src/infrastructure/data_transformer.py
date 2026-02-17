# take loaded data from data_loaders and transform it into the format needed for the application
import re

from src.utils.config_util import load_config
from .data_loaders import read_file, load_cbom


def transform_cbom_data(room_data:dict, data_12nc:dict,config:dict):
    """Transform raw CBOM data into structured mappings for rooms and 12NCs
    input:
    - room_data: dict with room numbers as keys and 12NCs with quantities as values
    - data_12nc: dict with 12NCs as keys and rooms with quantities as values
    - config: configuration dictionary for validation patterns and other settings

    output:
    - room_mappings: list of Room12NCMap objects
    - nc12_mappings: list of twelveNCRoomMap objects
    """
    if not room_data or not data_12nc:
        raise ValueError("Input data cannot be empty")
    
    if config is None:
        raise ValueError("Configuration cannot be None")
    
    room_mappings = []
    nc12_mappings = []

    # Validate and transform room data
    