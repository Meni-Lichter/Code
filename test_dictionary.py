"""Test script for dictionary loading functionality"""

from src.services.data_mangement import load_dictionary
from src.services.data_util import load_config
from tkinter import Tk, filedialog
import json

def main():
    print("="*80)
    print("Dictionary Reader Test")
    print("="*80)
    
    # Initialize tkinter for file picker
    root = Tk()
    root.withdraw()
    
    # File picker for dictionary
    print("\nPlease select a Dictionary Excel file...")
    dict_path = filedialog.askopenfilename(
        title="Select Dictionary Excel File",
        filetypes=[
            ("Excel files", "*.xlsx *.xls"),
            ("All files", "*.*")
        ]
    )
    
    if not dict_path:
        print("No file selected. Exiting.")
        return
    
    print(f"\nSelected file: {dict_path}")
    
    # Load dictionary
    print("\nLoading dictionary...")
    dict_mapping = load_dictionary(dict_path)
    
    if dict_mapping is None:
        print("Failed to load dictionary file.")
        return
    
    # Print results
    print("\n" + "="*80)
    print("DICTIONARY MAPPING RESULTS")
    print("="*80)
    
    print(f"\nTotal 12NC keys loaded: {len(dict_mapping)}")
    
    # Show first 10 mappings
    print("\n--- Sample Mappings (first 10) ---")
    for i, (key, values) in enumerate(list(dict_mapping.items())[:10]):
        print(f"\n12NC: {key}")
        print(f"  Mapped Items ({len(values)}): {', '.join(values)}")
    
    # Statistics
    total_mappings = sum(len(values) for values in dict_mapping.values())
    avg_mappings = total_mappings / len(dict_mapping) if dict_mapping else 0
    
    print("\n" + "="*80)
    print("STATISTICS")
    print("="*80)
    print(f"Total 12NC keys: {len(dict_mapping)}")
    print(f"Total mapped items: {total_mappings}")
    print(f"Average items per 12NC: {avg_mappings:.2f}")
    
    # Find 12NCs with most mappings
    if dict_mapping:
        max_mappings = max(len(values) for values in dict_mapping.values())
        max_12ncs = [key for key, values in dict_mapping.items() if len(values) == max_mappings]
        
        print(f"\n12NC(s) with most mappings ({max_mappings} items):")
        for key in max_12ncs[:5]:  # Show first 5
            print(f"  {key}: {', '.join(dict_mapping[key])}")
    
    print("\n✓ Test completed successfully!")

if __name__ == "__main__":
    main()