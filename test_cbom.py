"""Test script for CBOM reading functionality"""

from src.infrastructure import load_cbom
from src.utils import load_config
from tkinter import Tk, filedialog

def main():
    print("="*80)
    print("CBOM Reader Test")
    print("="*80)
    
    # Load configuration
    config = load_config('config/config.json')
    print("\nConfiguration loaded successfully")
    print("\nCBOM Settings:")
    for key, value in config.items():
        if key.startswith('cbom_'):
            print(f"  {key}: {value}")
    
    # Initialize file picker
    root = Tk()
    root.withdraw()
    
    print("\n" + "-"*80)
    print("Please select a CBOM Excel file...")
    cbom_path = filedialog.askopenfilename(
        title="Select CBOM Excel File",
        filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
    )
    
    if not cbom_path:
        print("No file selected. Exiting.")
        return
    
    print(f"\nReading file: {cbom_path}")
    print("-"*80)
    
    # Process CBOM file
    room_data, data_12nc = load_cbom(cbom_path, config)
    

    if room_data is not None and data_12nc is not None:
            
        """Print sample data from the dictionaries"""
        print("\n" + "="*80)
        print("SAMPLE DATA")
        print("="*80)
        
        if room_data:
            print(f"\n--- Sample Room Data (first {3} rooms) ---")
            for i, (room_num, df) in enumerate(list(room_data.items())[:3]):
                print(f"\nRoom: {room_num}")
                print(df.to_string(index=False))
        else:
            print("\nNo room data found!")
        
        if data_12nc:
            print(f"\n--- Sample 12NC Data (first {3} 12NCs) ---")
            for i, (nc12_num, df) in enumerate(list(data_12nc.items())[:3]):
                print(f"\n12NC: {nc12_num}")
                print(df.to_string(index=False))
        else:
            print("\nNo 12NC data found!")


        print("\n" + "="*80)
        print("✓ Test completed successfully!")
        print("="*80)
    else:
        print("\n" + "="*80)
        print("✗ Failed to read CBOM file")
        print("="*80)

if __name__ == "__main__":
    main()
