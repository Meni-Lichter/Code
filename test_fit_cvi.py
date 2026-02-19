"""Test script for FIT_CVI reading functionality"""

from src.utils import load_config
from src.infrastructure import read_file
from tkinter import Tk, filedialog
from pathlib import Path

def main():
    print("="*80)
    print("FIT_CVI Reader Test")
    print("="*80)
    
    # Load configuration
    config = load_config('config/config.json')
    print("\nConfiguration loaded successfully")
    print("\nFIT_CVI Settings:")
    fit_cvi_config = config.get('fit_cvi', {})
    for key, value in fit_cvi_config.items():
        print(f"  {key}: {value}")
    
    # Initialize file picker
    root = Tk()
    root.withdraw()
    
    print("\n" + "-"*80)
    print("Please select a FIT_CVI Excel file...")
    fit_cvi_path = filedialog.askopenfilename(
        title="Select FIT_CVI Excel File",
        filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
    )
    
    if not fit_cvi_path:
        print("No file selected. Exiting.")
        return
    
    print(f"\nReading file: {fit_cvi_path}")
    print("-"*80)
    
    # Process FIT_CVI file
    df = read_file(fit_cvi_path, file_type="fit_cvi", header=0)
    
    if df is not None:
        print(f"\n[OK] Successfully read file")
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
        
        # Check for expected FIT_CVI columns
        print("\n--- Column Validation ---")
        expected_cols = fit_cvi_config.get('columns', {})
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
    df_no_header = read_file(fit_cvi_path, file_type="fit_cvi", header=None)
    
    if df_no_header is not None:
        print(f"[OK] Successfully read file without headers")
        print(f"  Shape: {df_no_header.shape}")
        print(f"  Columns: {list(df_no_header.columns)}")
        print("\n--- First 3 Rows ---")
        print(df_no_header.head(3))

if __name__ == "__main__":
    main()
