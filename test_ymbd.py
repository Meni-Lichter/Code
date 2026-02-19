"""Test script for generic file reading functionality"""

from src.utils import load_config
from src.infrastructure import read_file
from tkinter import Tk, filedialog
from pathlib import Path

def main():
    print("="*80)
    print("Read File Test - YMBD")
    print("="*80)
    
    # Load configuration
    config = load_config('config/config.json')
    print("\nConfiguration loaded successfully")
    
    try:
        # Initialize file picker
        root = Tk()
        root.withdraw()
        
        print("\nPlease select a YMBD Excel file...")
        file_path = filedialog.askopenfilename(
            title="Select YMBD Excel File",
            filetypes=[
                ("Excel files", "*.xlsx *.xls *.xlsm"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            print("No file selected. Exiting.")
            return
    except KeyboardInterrupt:
        print ("something went wrong with file selection, exiting.")
        print("\nFile selection cancelled by user. Exiting.")
        return
    finally:
        root.destroy()
    
    print(f"\nSelected file: {file_path}")
    
    # Convert to Path object
    file_path = Path(file_path)
    
    # Test with header=0 (first row as headers)
    print("\n--- Test 1: Reading with header=0 (first row as column names) ---")
    df = read_file(file_path, file_type="ymbd", header=0)
    
    if df is not None:
        print(f"[OK] Successfully read file")
        print(f"  Shape: {df.shape} (rows: {df.shape[0]}, columns: {df.shape[1]})")
        print(f"  Columns: {list(df.columns)}")
        
        print("\n--- First 5 Rows ---")
        print(df.head())
        
        print("\n--- Data Types ---")
        print(df.dtypes)
        
        print("\n--- Sample Statistics ---")
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        if len(numeric_cols) > 0:
            print(f"Numeric columns found: {list(numeric_cols)}")
            print(df[numeric_cols].describe())
        
        # Check for expected YMBD columns
        print("\n--- Column Validation ---")
        ymbd_config = config.get('ymbd', {})
        expected_cols = ymbd_config.get('columns', {})
        
        if expected_cols:
            print("Expected columns from config:")
            for key, col_name in expected_cols.items():
                exists = col_name in df.columns
                status = "[OK]" if exists else "[MISSING]"
                print(f"  {status} {key}: '{col_name}'")
        
        print("\n[OK] Test completed successfully!")
    else:
        print("\n[ERROR] Failed to read file")
    
    # Test with header=None (no headers)
    print("\n" + "="*80)
    print("--- Test 2: Reading with header=None (no column names) ---")
    df_no_header = read_file(file_path, file_type="ymbd", header=None)
    
    if df_no_header is not None:
        print(f"[OK] Successfully read file without headers")
        print(f"  Shape: {df_no_header.shape}")
        print(f"  Columns: {list(df_no_header.columns)}")
        print("\n--- First 3 Rows ---")
        print(df_no_header.head(3))

if __name__ == "__main__":
    main()