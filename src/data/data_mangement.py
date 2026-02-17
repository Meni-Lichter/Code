##
#Data management functions for the Room-12NC Performance Center application
##

# Standard library imports
import pandas as pd
import tkinter as tk
import re
import logging
# Use relative imports for functions from data_utility
from ..utils.data_util import (
    col_letter_to_index,
    file_in_use,
    normalize_identifier,
    find_column_by_canon,
    load_config, 
    pick_sheet,
    read_file
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_cbom(cbom_path, config):
    """
    Reads the CBOM Excel file and extracts room-12NC relationships.
      
    Input:
    - cbom_path: Path to the CBOM Excel file
    - config: Configuration dictionary with CBOM structure settings
    
    Output:
    - room_data: Dictionary {room_number: DataFrame['12NC (normalized)', '12NC (original)', '12NC_Description', 'Quantity']}
    - data_12nc: Dictionary {12nc_number: DataFrame['Room(normalized)','Room(original)', 'Room_Description', 'Quantity']}
    """
    
    # Get configuration values
    room_col_start = config["cbom"]["columns"].get("room_start","G") 
    room_num_row = config["cbom"]["rows"].get("room_numbers", 5)
    room_desc_row = config["cbom"]["rows"].get("room_descriptions", 4)
    nc12_col = config["cbom"]["columns"].get("12nc", 'C')
    nc12_desc_col = config["cbom"]["columns"].get("12nc_description", 'D')
    nc12_row_start = config["cbom"]["rows"].get("12nc_start", 9)
    
    df = read_file(cbom_path, "cbom" , header=None)
    if df is None:
        return None, None
    
    room_col_idx = col_letter_to_index(room_col_start)
    nc12_col_idx = col_letter_to_index(nc12_col)
    nc12_desc_col_idx = col_letter_to_index(nc12_desc_col)
    
    # Convert 1-indexed rows to 0-indexed
    room_num_row_idx = room_num_row - 1
    room_desc_row_idx = room_desc_row - 1
    nc12_row_start_idx = nc12_row_start - 1
    
    # Extract room information (starting from room_col_start)
    room_numbers = df.iloc[room_num_row_idx, room_col_idx:].values 
    room_descriptions = df.iloc[room_desc_row_idx, room_col_idx:].values
    
    # Extract 12NC information (starting from nc12_row_start)
    nc12_numbers = df.iloc[nc12_row_start_idx:, nc12_col_idx].values
    nc12_descriptions = df.iloc[nc12_row_start_idx:, nc12_desc_col_idx].values
    
    # Extract the quantity matrix (from nc12_row_start, room columns onwards)
    quantity_matrix = df.iloc[nc12_row_start_idx:, room_col_idx:].values
    
    # Initialize dictionaries to hold data
    room_data = {}
    data_12nc = {}
    
    ############################
    # Process data for each room
    ############################
    valid_room_count = 0
    for room_idx, room_num in enumerate(room_numbers):
        if pd.isna(room_num):
            continue
        
        room_num_normalized = normalize_identifier(room_num)
        
        if not room_num_normalized:  # Skip empty normalized values
            continue
        
        valid_room_count += 1 
        # Collect all 12NCs for this room
        room_12ncs = []
        for nc12_idx, nc12_num in enumerate(nc12_numbers):
            if pd.isna(nc12_num):
                continue
                
            nc12_num_normalized = normalize_identifier(nc12_num)
            
            # Validate normalized format (12 digits)
            if (not re.match(config["validation"]["patterns"]["12nc_normalized"], nc12_num_normalized)) or (not nc12_num_normalized):
                continue
            
            quantity = quantity_matrix[nc12_idx, room_idx]
            
            # Only include if quantity exists and is not zero
            if not pd.isna(quantity) and quantity != 0:
                nc12_desc = str(nc12_descriptions[nc12_idx]).strip() if not pd.isna(nc12_descriptions[nc12_idx]) else ""
                
                room_12ncs.append({
                    '12NC': nc12_num_normalized,  # Store normalized version
                    '12NC_Original': str(nc12_num).strip(),  # Keep original for reference
                    '12NC_Description': nc12_desc,
                    'Quantity': quantity
                })
        
        # Create DataFrame for this room (use normalized room number as key)
        if room_12ncs:
            room_data[room_num_normalized] = pd.DataFrame(room_12ncs)
    

    ############################
    # Process data for each 12NC
    ############################
    valid_12nc_count = 0
    for nc12_idx, nc12_num in enumerate(nc12_numbers):
        if pd.isna(nc12_num):
            continue
        
        nc12_num_str = str(nc12_num).strip()
        
        nc12_num_normalized = normalize_identifier(nc12_num_str)
        
        # Validate normalized format (12 digits)
        if not re.match(config["validation"]["patterns"]["12nc_normalized"], nc12_num_normalized):
            continue
        
        valid_12nc_count += 1
        nc12_desc = str(nc12_descriptions[nc12_idx]).strip() if not pd.isna(nc12_descriptions[nc12_idx]) else ""
        
        # Collect all rooms for this 12NC
        nc12_rooms = []
        for room_idx, room_num in enumerate(room_numbers):
            if pd.isna(room_num):
                continue
            room_num_normalized = normalize_identifier(room_num)
                
            if (not room_num_normalized):  # Skip empty normalized values
                continue
            
            quantity = quantity_matrix[nc12_idx, room_idx]
            
            if not pd.isna(quantity) and quantity != 0:    
                room_desc = str(room_descriptions[room_idx]).strip() if not pd.isna(room_descriptions[room_idx]) else ""
                
                nc12_rooms.append({
                    'Room': room_num_normalized,  # Store normalized version
                    'Room_Original': str(room_num).strip(),  # Keep original for reference
                    'Room_Description': room_desc,
                    'Quantity': quantity
                })
        
        # Create DataFrame for this 12NC (use normalized 12NC as key)
        if nc12_rooms:
            data_12nc[nc12_num_normalized] = pd.DataFrame(nc12_rooms)
    
    return room_data, data_12nc






