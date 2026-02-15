"""
Test script for updating relevant_rooms in config from an Excel file
"""

import sys
import os
from tkinter import Tk, filedialog

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.config_util import load_config, update_relevant_rooms
from src.services.data_util import read_file, load_config

def main():
    """Test updating relevant_rooms from Excel file"""
    
    print("=" * 80)
    print("TEST: Update Relevant Rooms from Excel File")
    print("=" * 80)
    
    # Load config
    config = load_config('config.json')
    print("\n1. Config loaded successfully")
    
    # Show current relevant rooms
    current_rooms = config.get("relevant_rooms", {}).get("rooms", [])
    print(f"\n2. Current relevant_rooms count: {len(current_rooms)}")
    if current_rooms:
        print(f"   Sample rooms: {current_rooms[:5]}")
    
    # Select Excel file with room data
    print("\n3. Please select an Excel file containing room data...")
    root = Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    
    file_path = filedialog.askopenfilename(
        title="Select Excel file with room data",
        filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
    )
    root.destroy()
    
    if not file_path:
        print("No file selected. Exiting...")
        return
    
    print(f"\n4. Selected file: {file_path}")
    
    # Read the Excel file
    print("\n5. Reading Excel file...")
    df = read_file(file_path, 'fit_cvi', config)  # Using fit_cvi config as it has room column
    
    if df is None or df.empty:
        print("ERROR: Failed to read file or file is empty")
        return
    
    print(f"   Loaded {len(df)} rows")
    print(f"   Columns: {list(df.columns)}")
    
    # Extract unique rooms from the DataFrame
    # Assuming the room column is named 'Room' after reading with fit_cvi config
    room_column = 'Room'  # Adjust if your column name is different
    
    if room_column not in df.columns:
        print(f"\nERROR: Column '{room_column}' not found in file")
        print(f"Available columns: {list(df.columns)}")
        return
    
    # Get unique rooms and remove any NaN/None values
    rooms_from_file = df[room_column].dropna().unique().tolist()
    print(f"\n6. Extracted {len(rooms_from_file)} unique rooms from file")
    print(f"   Sample rooms: {rooms_from_file[:10]}")
    
    # Ask for confirmation
    print("\n7. Do you want to update the config with these rooms? (y/n)")
    response = input("   > ").strip().lower()
    
    if response != 'y':
        print("Update cancelled.")
        return
    
    # Update the config
    print("\n8. Updating config...")
    update_relevant_rooms(rooms_from_file, 'config.json')
    
    # Verify the update
    updated_config = load_config('config.json')
    updated_rooms = updated_config.get("relevant_rooms", {}).get("rooms", [])
    print(f"\n9. Update complete!")
    print(f"   New relevant_rooms count: {len(updated_rooms)}")
    print(f"   Sample rooms: {updated_rooms[:10]}")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
