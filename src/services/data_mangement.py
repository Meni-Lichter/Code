import pandas as pd
import tkinter as tk
from tkinter import Tk, filedialog, messagebox, simpledialog
import os
import re
from datetime import datetime
import sys
from collections import OrderedDict
import json
import logging

from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use relative imports for functions from data_utility
from .data_utility import (
    col_letter_to_index,
    normalize_identifier,
    find_column_by_canon,
    load_config, pick_sheet
)

# ---------- REGEX PATTERNS ----------
KEY_REGEX = r"^\d{4} \d{3} \d{5}$" # Matches "1234 567 89123"
VALUE_REGEX = r"^[A-Z]{3,4}\d+$" # Matches "ABC123", "ABCD4567", etc.


def load_dictionary(dict_path):
    """
    Loads dictionary Excel from sheet named '12NC_Mapping' into a mapping:
        key → list of values
    Validates key and value formats.
    """
    try:
        # Read only the sheet named '12NC_Mapping'
        df_dict = pd.read_excel(dict_path, sheet_name="12NC_Mapping")
    except PermissionError as e:
        logger.error(f"Could not open the dictionary file due to a permission error: {e}")
        messagebox.showerror(
            "Permission Error",
            f"Could not open the dictionary file due to a permission error:\n\n{e}\n\n"
            "Please close the file if it is open in another program and try again."
        )
        return None
    except ValueError as e: # Sheet not found or file not readable
        messagebox.showerror(
            "Error",
            f"Could not read dictionary file:\n{e}\n\n"
            "Please ensure the file is a valid Excel file and contains a sheet named '12NC_Mapping'."
        )
        return None
    except Exception as e: # Any other read error
        messagebox.showerror(
            "Error",
            f"Could not read dictionary file:\n{e}"
        )
        return None
    
    required_columns = {"12NC", "Mapped Items"}
    if not required_columns.issubset(set(df_dict.columns)):
        messagebox.showerror(
            "Error",
            f"Sheet '12NC_Mapping' must contain columns: {required_columns}"
        )
        return None

    dict_mapping = {}
    invalid_keys = []
    invalid_values = []

    for _, row in df_dict.iterrows():
        key = str(row["12NC"]).strip()

        # validate key format
        if not re.match(KEY_REGEX, key):# Matches "1234 567 89123"
            invalid_keys.append(key)

        values_str = str(row["Mapped Items"]).strip() if not pd.isna(row["Mapped Items"]) else ""
        values_list = [v.strip() for v in values_str.split(",")] if values_str else [] # Split by commas

        for v in values_list:
            if not re.match(VALUE_REGEX, v):# Matches "ABC123", "ABCD4567", etc.
                invalid_values.append(v)

        dict_mapping[key] = values_list 

    errors = []
    if invalid_keys:
        errors.append(f"Invalid keys:\n" + "\n".join(invalid_keys[:10]))
    if invalid_values:
        errors.append(f"Invalid values:\n" + "\n".join(invalid_values[:10]))

    if errors:# If there are any validation errors
        messagebox.showerror("Validation Error", "\n\n".join(errors) + "\n\nPlease check the dictionary file.")
        return None

    return dict_mapping

 

def read_CBOM(cbom_path, config):
    """
    Reads the CBOM Excel file and extracts room-12NC relationships.
      
    Input:
    - cbom_path: Path to the CBOM Excel file
    - config: Configuration dictionary with CBOM structure settings
    
    Output:
    - room_data: Dictionary {room_number: DataFrame['12NC', '12NC_Description', 'Quantity']}
    - data_12nc: Dictionary {12nc_number: DataFrame['Room', 'Room_Description', 'Quantity']}
    """
    # Regex pattern for valid 12NC format: ####-###-#####
    NC12_FORMAT_REGEX = r"^\d{4}-\d{3}-\d{5}$"
     # After normalization: 12 consecutive digits
    NC12_NORMALIZED_REGEX = r"^\d{12}$"
    
    # Get configuration values
    room_col_start = config.get('cbom_room_col_start', 'G')
    room_num_row = config.get('cbom_room_num_row', 5)
    room_desc_row = config.get('cbom_room_desc_row', 4)
    nc12_col = config.get('cbom_12nc_col', 'C')
    nc12_desc_col = config.get('cbom_12nc_desc_col', 'D')
    nc12_row_start = config.get('cbom_12nc_row_start', 9)
    
    try:
        # Read the Excel file without headers
    #TODO : ADD CHECKING IF FILE IS OPEN / EXISTS BEFORE TRYING TO READ, TO AVOID UNNECESSARY ERROR POPUPS
        df = pd.read_excel(cbom_path, header=None)
    except PermissionError as e:
        messagebox.showerror(
            "Permission Error",
            f"Could not open the CBOM file due to a permission error:\n\n{e}\n\n"
            "Please close the file if it is open in another program and try again."
        )
        return None, None
    except Exception as e:
        messagebox.showerror(
            "Error",
            f"Could not read CBOM file:\n{e}"
        )
        return None, None
    
    
    room_col_idx = col_letter_to_index(room_col_start)
    nc12_col_idx = col_letter_to_index(nc12_col)
    nc12_desc_col_idx = col_letter_to_index(nc12_desc_col)
    
    # Convert 1-indexed rows to 0-indexed
    room_num_row_idx = room_num_row - 1
    room_desc_row_idx = room_desc_row - 1
    nc12_row_start_idx = nc12_row_start - 1
    
    # Extract room information (starting from room_col_start)
    room_numbers = df.iloc[room_num_row_idx, room_col_idx:].values #
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
    for room_idx, room_num in enumerate(room_numbers):
        if pd.isna(room_num):
            continue
        
        room_num_str = str(room_num).strip()
        room_num_normalized = normalize_identifier(room_num_str)
        
        if not room_num_normalized:  # Skip empty normalized values
            continue
        
        room_desc = str(room_descriptions[room_idx]).strip() if not pd.isna(room_descriptions[room_idx]) else ""
        
        # Collect all 12NCs for this room
        room_12ncs = []
        for nc12_idx, nc12_num in enumerate(nc12_numbers):
            if pd.isna(nc12_num):
                continue
            
            nc12_num_str = str(nc12_num).strip()
            
            # Validate 12NC format (####-###-#####)
            if not re.match(NC12_FORMAT_REGEX, nc12_num_str):
                continue
            
            nc12_num_normalized = normalize_identifier(nc12_num_str)
            
            # Validate normalized format (12 digits)
            if not re.match(NC12_NORMALIZED_REGEX, nc12_num_normalized):
                continue
            
            quantity = quantity_matrix[nc12_idx, room_idx]
            
            # Only include if quantity exists and is not zero
            if not pd.isna(quantity) and quantity != 0:
                nc12_desc = str(nc12_descriptions[nc12_idx]).strip() if not pd.isna(nc12_descriptions[nc12_idx]) else ""
                
                room_12ncs.append({
                    '12NC': nc12_num_normalized,  # Store normalized version
                    '12NC_Original': nc12_num_str,  # Keep original for reference
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
        
        # Validate 12NC format (####-###-#####)
        if not re.match(NC12_FORMAT_REGEX, nc12_num_str):
            continue
        
        nc12_num_normalized = normalize_identifier(nc12_num_str)
        
        # Validate normalized format (12 digits)
        if not re.match(NC12_NORMALIZED_REGEX, nc12_num_normalized):
            continue
        
        valid_12nc_count += 1
        nc12_desc = str(nc12_descriptions[nc12_idx]).strip() if not pd.isna(nc12_descriptions[nc12_idx]) else ""
        
        # Collect all rooms for this 12NC
        nc12_rooms = []
        for room_idx, room_num in enumerate(room_numbers):
            if pd.isna(room_num):
                continue
            
            quantity = quantity_matrix[nc12_idx, room_idx]
            
            # Only include if quantity exists and is greater than 0
            if not pd.isna(quantity) and quantity != 0:
                room_num_str = str(room_num).strip()
                room_num_normalized = normalize_identifier(room_num_str)
                
                if not room_num_normalized:  # Skip empty normalized values
                    continue
                
                room_desc = str(room_descriptions[room_idx]).strip() if not pd.isna(room_descriptions[room_idx]) else ""
                
                nc12_rooms.append({
                    'Room': room_num_normalized,  # Store normalized version
                    'Room_Original': room_num_str,  # Keep original for reference
                    'Room_Description': room_desc,
                    'Quantity': quantity
                })
        
        # Create DataFrame for this 12NC (use normalized 12NC as key)
        if nc12_rooms:
            data_12nc[nc12_num_normalized] = pd.DataFrame(nc12_rooms)
    
    return room_data, data_12nc


# Load Excel with dtype=str, fillna("") 
def load_excel(path: Path, mode: int = 1) -> pd.DataFrame:
    """
    Read Excel files (.xlsx, .xlsm) depending on mode:
    - mode=1: full load with dtype=str
    - mode=0: header-only (nrows=0)
    Automatically picks the correct sheet depending on file_type:
    - Leading → first sheet not named 'Summary'
    - IH10 / IW75 → 'Sheet1' if exists, else first
    """
    try:
        chosen = pick_sheet(path)

        if mode == 1:
            # Read with string dtype directly to avoid double conversion
            df = pd.read_excel(
                path, 
                engine="openpyxl", 
                sheet_name=chosen, 
                header=0, 
                dtype=str,  # Use str for consistency
                keep_default_na=False  # Prevents NaN creation
            )
            return df.fillna("")  # Just in case some NaNs slip through

        elif mode == 0:
            # Header-only read with consistent string typing
            df = pd.read_excel(
                path, 
                engine="openpyxl", 
                sheet_name=chosen, 
                nrows=0,
                dtype=str  # Consistent with mode 1
            )
            return df
        
        else:
            raise ValueError(f"Invalid mode={mode}. Expected 0 (headers only) or 1 (full read).")

    except FileNotFoundError:
        raise ValueError(f"File not found: {path}")
    except Exception as e:
        msg = (
            f"Error loading info from sheet '{chosen if 'chosen' in locals() else 'unknown'}'\n\n"
            f"File: {path.name}\n\n"
            f"Error: {str(e)}"
        )
        raise ValueError(msg) from e  # Preserve original exception chain


## FOR TESTING PURPOSES: PRINT SAMPLE DATA
def print_sample_data(room_data, data_12nc, num_samples=50):
    """Print sample data from the dictionaries"""
    print("\n" + "="*80)
    print("SAMPLE DATA")
    print("="*80)
    
    if room_data:
        print(f"\n--- Sample Room Data (first {num_samples} rooms) ---")
        for i, (room_num, df) in enumerate(list(room_data.items())[:num_samples]):
            print(f"\nRoom: {room_num}")
            print(df.to_string(index=False))
    else:
        print("\nNo room data found!")
    
    if data_12nc:
        print(f"\n--- Sample 12NC Data (first {num_samples} 12NCs) ---")
        for i, (nc12_num, df) in enumerate(list(data_12nc.items())[:num_samples]):
            print(f"\n12NC: {nc12_num}")
            print(df.to_string(index=False))
    else:
        print("\nNo 12NC data found!")


