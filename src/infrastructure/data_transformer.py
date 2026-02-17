# take loaded data from data_loaders and transform it into the format needed for the application
import re

from src.models.mapping import Room12NCMap, TwelveNCRoomMap
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
    - nc12_mappings: list of TwelveNCRoomMap objects
    """
    if not room_data or not data_12nc:
        raise ValueError("Input data cannot be empty")
    
    if config is None:
        raise ValueError("Configuration cannot be None")
    
    room_mappings = []
    nc12_mappings = []

    # Validate and transform room data
    for room, twelve_ncs in room_data.items():
        if not re.match(config["validation"]["patterns"]["room_normalized"], room):
            print(f"Warning: Room '{room}' does not match expected format. Skipping.")
            continue
        
        valid_twelve_ncs = {nc: qty for nc, qty in twelve_ncs.items() 
                            if re.match(config["validation"]["patterns"]["12nc_normalized"], nc)}
        
        if not valid_twelve_ncs:
            print(f"Warning: No valid 12NCs found for room '{room}'. Skipping.")
            continue
        
        room_mappings.append(Room12NCMap(room=room, twelve_ncs=valid_twelve_ncs))
    
    # Validate and transform 12NC data
    for nc12, rooms in data_12nc.items():
        if not re.match(config["validation"]["patterns"]["12nc_normalized"], nc12):
            print(f"Warning: 12NC '{nc12}' does not match expected format. Skipping.")
            continue
        valid_rooms = {room: qty for room, qty in rooms.items() 
                       if re.match(config["validation"]["patterns"]["room_normalized"], room)}
        if not valid_rooms:
            print(f"Warning: No valid rooms found for 12NC '{nc12}'. Skipping.")
            continue
        nc12_mappings.append(TwelveNCRoomMap(twelve_nc=nc12, rooms=valid_rooms))

    return room_mappings, nc12_mappings