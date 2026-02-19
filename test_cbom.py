"""Test script for CBOM reading functionality"""

from logging import root

from pathlib import Path
from typing import List, Optional

from src.infrastructure import load_cbom
from src.utils import load_config
from tkinter import Tk, filedialog


def pick_file():
    root = Tk()
    root.withdraw()  # hide main window
    root.attributes("-topmost", True)  # bring dialog to front
    root.update()  # ensure it becomes active

    path = filedialog.askopenfilename(title="Select a file", filetypes=[("All files", "*.*")])

    root.destroy()

    if not path:  # '' means dialog returned nothing (cancel or failed)
        raise RuntimeError("No file selected (dialog returned empty path).")

    return path


def main():
    print("=" * 80)
    print("CBOM Reader Test")
    print("=" * 80)

    # Load configuration
    config = load_config("config/config.json")
    print("\nConfiguration loaded successfully")
    print("\nCBOM Settings:")

    # Display CBOM configuration properly
    cbom_config = config.get("cbom", {})
    if cbom_config:
        print(f"  Description: {cbom_config.get('description', 'N/A')}")
        print(f"  Columns: {cbom_config.get('columns', {})}")
        print(f"  Rows: {cbom_config.get('rows', {})}")
        print(f"  Target Sheet: {cbom_config.get('target_sheet', {})}")

    print("\n" + "-" * 80)
    print("Please select a CBOM Excel file...")

    try:
        cbom_path = pick_file()

    except Exception as e:
        print(f"\nError opening file dialog: {e}")
        return
    finally:
        try:
            root.destroy()
        except:
            pass

    if not cbom_path:
        print("No file selected. Exiting.")
        return

    print(f"\nReading file: {cbom_path}")
    print("-" * 80)

    if isinstance(cbom_path, str):
        cbom_path = Path(cbom_path)
    # Process CBOM file
    room_data, data_12nc = load_cbom(cbom_path, config)

    if room_data is not None and data_12nc is not None:

        """Print sample data from the dictionaries"""
        print("\n" + "=" * 80)
        print("SAMPLE DATA")
        print("=" * 80)

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

        print("\n" + "=" * 80)
        print("[OK] Test completed successfully!")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("[ERROR] Failed to read CBOM file")
        print("=" * 80)


if __name__ == "__main__":
    main()
