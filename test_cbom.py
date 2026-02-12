"""Test script for CBOM reading functionality"""

from src.services import read_CBOM, print_sample_data, load_config
from tkinter import Tk, filedialog

def main():
    print("="*80)
    print("CBOM Reader Test")
    print("="*80)
    
    # Load configuration
    config = load_config('config.json')
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
    room_data, data_12nc = read_CBOM(cbom_path, config)
    
    if room_data is not None and data_12nc is not None:
        print_sample_data(room_data, data_12nc, num_samples=3)
        print("\n" + "="*80)
        print("✓ Test completed successfully!")
        print("="*80)
    else:
        print("\n" + "="*80)
        print("✗ Failed to read CBOM file")
        print("="*80)

if __name__ == "__main__":
    main()
