"""
Infrastructure Test Suite for Room_12NC_PerformanceCenter
Tests data loading and transformation performance and accuracy.
"""

import pytest
import pandas as pd
import time
from pathlib import Path
from tkinter import Tk, filedialog
from typing import Optional, Tuple

# Import infrastructure modules
from src.infrastructure.data_loaders import load_cbom, read_file
from src.infrastructure.data_transformer import (
    transform_cbom_data,
    parse_ymbd_to_sales_records,
    parse_fit_cvi_to_sales_records,
)
from src.models.mapping import Room, TwelveNC
from src.models.sales_record import SalesRecord
from src.utils.config_util import load_config


# ============================================================================
# FILE PICKER UTILITIES
# ============================================================================


def pick_file(title: str, filetypes: list) -> Optional[str]:
    """Open file picker dialog"""
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    file_path = filedialog.askopenfilename(title=title, filetypes=filetypes)
    root.destroy()

    return file_path if file_path else None


def get_test_files() -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Interactive file selection for test files"""
    print("\n" + "=" * 80)
    print("📂 FILE SELECTION FOR INFRASTRUCTURE TESTS")
    print("=" * 80)

    print("\n1️⃣  Select CBOM file (Excel)...")
    cbom_file = pick_file(
        "Select CBOM File", [("Excel files", "*.xlsx *.xlsm *.xls"), ("All files", "*.*")]
    )
    if cbom_file:
        print(f"   ✓ Selected: {Path(cbom_file).name}")
    else:
        print("   ⚠ Skipped")

    print("\n2️⃣  Select YMBD file (Excel)...")
    ymbd_file = pick_file(
        "Select YMBD File", [("Excel files", "*.xlsx *.xlsm *.xls"), ("All files", "*.*")]
    )
    if ymbd_file:
        print(f"   ✓ Selected: {Path(ymbd_file).name}")
    else:
        print("   ⚠ Skipped")

    print("\n3️⃣  Select FIT/CVI file (Excel)...")
    fit_file = pick_file(
        "Select FIT/CVI File", [("Excel files", "*.xlsx *.xlsm *.xls"), ("All files", "*.*")]
    )
    if fit_file:
        print(f"   ✓ Selected: {Path(fit_file).name}")
    else:
        print("   ⚠ Skipped")

    print("\n" + "=" * 80 + "\n")

    return cbom_file, ymbd_file, fit_file


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture(scope="session")
def test_files():
    """Session-scoped fixture for test files"""
    return get_test_files()


@pytest.fixture
def cbom_file(test_files):
    """CBOM file path fixture"""
    return test_files[0]


@pytest.fixture
def ymbd_file(test_files):
    """YMBD file path fixture"""
    return test_files[1]


@pytest.fixture
def fit_file(test_files):
    """FIT/CVI file path fixture"""
    return test_files[2]


@pytest.fixture(scope="session")
def config():
    """Load configuration"""
    return load_config()


# ============================================================================
# DATA LOADER TESTS
# ============================================================================


class TestDataLoaders:
    """Test suite for data loading functions"""

    def test_load_cbom(self, cbom_file, config):
        """Test CBOM file loading performance and structure"""
        if not cbom_file:
            pytest.skip("No CBOM file provided")

        print("\n" + "=" * 80)
        print("🧪 TEST: CBOM File Loading")
        print("=" * 80)

        start_time = time.perf_counter()

        # Load CBOM file
        room_data, data_12nc = load_cbom(cbom_file, config)

        end_time = time.perf_counter()
        load_time = (end_time - start_time) * 1000  # ms

        # Assertions
        assert room_data is not None, "room_data should not be None"
        assert data_12nc is not None, "data_12nc should not be None"
        assert isinstance(room_data, dict), "room_data should be a dictionary"
        assert isinstance(data_12nc, dict), "data_12nc should be a dictionary"
        assert len(room_data) > 0, "Should load at least one room"
        assert len(data_12nc) > 0, "Should load at least one 12NC"

        # Performance metrics
        total_items = len(room_data) + len(data_12nc)
        throughput = total_items / (load_time / 1000) if load_time > 0 else 0

        print(f"\n✓ CBOM file loaded successfully")
        print(f"  - File: {Path(cbom_file).name}")
        print(f"  - Load time: {load_time:.2f} ms")
        print(f"  - Rooms loaded: {len(room_data):,}")
        print(f"  - 12NCs loaded: {len(data_12nc):,}")
        print(f"  - Throughput: {throughput:.2f} items/sec")

        # Data structure validation
        print(f"\n📊 Data Structure:")
        # Check first room
        first_room_key = next(iter(room_data.keys()))
        first_room_data = room_data[first_room_key]
        print(f"  - Sample room: {first_room_key}")
        print(f"    Type: {type(first_room_data)}")
        print(f"    12NCs in room: {len(first_room_data)}")

        # Check first 12NC
        first_12nc_key = next(iter(data_12nc.keys()))
        first_12nc_data = data_12nc[first_12nc_key]
        print(f"  - Sample 12NC: {first_12nc_key}")
        print(f"    Type: {type(first_12nc_data)}")
        print(f"    Rooms with 12NC: {len(first_12nc_data)}")

        print("\n" + "=" * 80)

    def test_load_ymbd(self, ymbd_file):
        """Test YMBD file loading performance"""
        if not ymbd_file:
            pytest.skip("No YMBD file provided")

        print("\n" + "=" * 80)
        print("🧪 TEST: YMBD File Loading")
        print("=" * 80)

        start_time = time.perf_counter()

        # Load YMBD file
        ymbd_df = read_file(ymbd_file, "ymbd", header=0)

        end_time = time.perf_counter()
        load_time = (end_time - start_time) * 1000

        # Assertions
        assert ymbd_df is not None, "DataFrame should not be None"
        assert isinstance(ymbd_df, pd.DataFrame), "Should return pandas DataFrame"
        assert len(ymbd_df) > 0, "DataFrame should not be empty"

        # Performance metrics
        rows = len(ymbd_df)
        throughput = rows / (load_time / 1000) if load_time > 0 else 0

        print(f"\n✓ YMBD file loaded successfully")
        print(f"  - File: {Path(ymbd_file).name}")
        print(f"  - Load time: {load_time:.2f} ms")
        print(f"  - Rows loaded: {rows:,}")
        print(f"  - Columns: {len(ymbd_df.columns)}")
        print(f"  - Throughput: {throughput:.2f} rows/sec")

        print(f"\n📊 Data Quality:")
        print(f"  - Null values: {ymbd_df.isnull().sum().sum()}")
        print(f"  - Duplicate rows: {ymbd_df.duplicated().sum()}")
        print(f"  - Column names: {list(ymbd_df.columns[:5])}")

        print("\n" + "=" * 80)

    def test_load_fit_cvi(self, fit_file):
        """Test FIT/CVI file loading performance"""
        if not fit_file:
            pytest.skip("No FIT/CVI file provided")

        print("\n" + "=" * 80)
        print("🧪 TEST: FIT/CVI File Loading")
        print("=" * 80)

        start_time = time.perf_counter()

        # Load FIT/CVI file
        fit_df = read_file(fit_file, "fit_cvi", header=0)

        end_time = time.perf_counter()
        load_time = (end_time - start_time) * 1000

        # Assertions
        assert fit_df is not None, "DataFrame should not be None"
        assert isinstance(fit_df, pd.DataFrame), "Should return pandas DataFrame"
        assert len(fit_df) > 0, "DataFrame should not be empty"

        # Performance metrics
        rows = len(fit_df)
        throughput = rows / (load_time / 1000) if load_time > 0 else 0

        print(f"\n✓ FIT/CVI file loaded successfully")
        print(f"  - File: {Path(fit_file).name}")
        print(f"  - Load time: {load_time:.2f} ms")
        print(f"  - Rows loaded: {rows:,}")
        print(f"  - Columns: {len(fit_df.columns)}")
        print(f"  - Throughput: {throughput:.2f} rows/sec")

        print(f"\n📊 Data Quality:")
        print(f"  - Null values: {fit_df.isnull().sum().sum()}")
        print(f"  - Duplicate rows: {fit_df.duplicated().sum()}")
        print(f"  - Column names: {list(fit_df.columns[:5])}")

        print("\n" + "=" * 80)


# ============================================================================
# DATA TRANSFORMER TESTS
# ============================================================================


class TestDataTransformers:
    """Test suite for data transformation functions"""

    def test_transform_cbom_data(self, cbom_file, config):
        """Test CBOM data transformation to Room and TwelveNC objects"""
        if not cbom_file:
            pytest.skip("No CBOM file provided")

        print("\n" + "=" * 80)
        print("🧪 TEST: CBOM Data Transformation")
        print("=" * 80)

        # Load CBOM data first
        print("\n📥 Loading CBOM...")
        room_data, data_12nc = load_cbom(cbom_file, config)
        print(f"  ✓ Loaded {len(room_data)} rooms, {len(data_12nc)} 12NCs")

        # Transform data
        print("\n🔄 Transforming data...")
        start_time = time.perf_counter()

        rooms, nc12s = transform_cbom_data(room_data, data_12nc, config)

        end_time = time.perf_counter()
        transform_time = (end_time - start_time) * 1000

        # Assertions
        assert rooms is not None, "rooms should not be None"
        assert nc12s is not None, "nc12s should not be None"
        assert isinstance(rooms, list), "rooms should be a list"
        assert isinstance(nc12s, list), "nc12s should be a list"
        assert len(rooms) > 0, "Should create at least one room"
        assert len(nc12s) > 0, "Should create at least one 12NC"
        assert all(isinstance(r, Room) for r in rooms), "All items should be Room objects"
        assert all(isinstance(nc, TwelveNC) for nc in nc12s), "All items should be TwelveNC objects"

        # Performance metrics
        total_objects = len(rooms) + len(nc12s)
        throughput = total_objects / (transform_time / 1000) if transform_time > 0 else 0

        print(f"\n✓ CBOM data transformed successfully")
        print(f"  - Transform time: {transform_time:.2f} ms")
        print(f"  - Room objects created: {len(rooms):,}")
        print(f"  - TwelveNC objects created: {len(nc12s):,}")
        print(f"  - Throughput: {throughput:.2f} objects/sec")

        # Validate structure
        print(f"\n📦 Sample Room Object:")
        sample_room = rooms[0]
        print(f"  - Room ID: {sample_room.id}")
        desc = sample_room.description
        print(f"  - Description: {desc[:50]}..." if len(desc) > 50 else f"  - Description: {desc}")
        print(f"  - Components: {len(sample_room.twelve_ncs)}")
        print(f"  - Total items: {sample_room.total_items}")

        print(f"\n🔢 Sample 12NC Object:")
        sample_12nc = nc12s[0]
        print(f"  - 12NC ID: {sample_12nc.id}")
        desc = sample_12nc.description
        print(f"  - Description: {desc[:50]}..." if len(desc) > 50 else f"  - Description: {desc}")
        print(f"  - IGT: {sample_12nc.igt}")
        print(f"  - Rooms: {len(sample_12nc.rooms)}")
        print(f"  - Total items: {sample_12nc.total_items}")

        # Validation checks
        print(f"\n🔍 Validation:")
        invalid_room_ids = [r for r in rooms if not r.id]
        invalid_12ncs = [nc for nc in nc12s if not nc.id or len(nc.id) != 12]
        print(f"  ✓ Rooms with valid IDs: {len(rooms) - len(invalid_room_ids)}/{len(rooms)}")
        print(f"  ✓ 12NCs with valid IDs: {len(nc12s) - len(invalid_12ncs)}/{len(nc12s)}")

        assert len(invalid_room_ids) == 0, "All rooms should have IDs"
        assert len(invalid_12ncs) == 0, "All 12NCs should have valid 12-digit IDs"

        print("\n" + "=" * 80)

    def test_parse_ymbd_to_sales_records(self, cbom_file, ymbd_file, config):
        """Test YMBD parsing and linking to TwelveNC objects"""
        if not cbom_file or not ymbd_file:
            pytest.skip("Need both CBOM and YMBD files")

        print("\n" + "=" * 80)
        print("🧪 TEST: YMBD Sales Record Parsing")
        print("=" * 80)

        # Setup: Load and transform CBOM first
        print("\n📥 Setup: Loading CBOM...")
        room_data, data_12nc = load_cbom(cbom_file, config)
        rooms, nc12s = transform_cbom_data(room_data, data_12nc, config)
        print(f"  ✓ Created {len(nc12s)} 12NC objects")

        # Load YMBD data
        print("\n📥 Loading YMBD...")
        ymbd_df = read_file(ymbd_file, "ymbd", header=0)
        print(f"  ✓ Loaded {len(pd.DataFrame(ymbd_df))} YMBD rows")

        # Parse YMBD and update 12NCs
        print("\n🔄 Parsing YMBD to sales records...")
        start_time = time.perf_counter()

        updated_nc12s = parse_ymbd_to_sales_records(nc12s, ymbd_df)

        end_time = time.perf_counter()
        parse_time = (end_time - start_time) * 1000

        # Assertions
        assert updated_nc12s is not None, "Should not return None"
        assert len(updated_nc12s) == len(nc12s), "Should return same number of 12NCs"

        # Count 12NCs with sales data
        nc12s_with_sales = [nc for nc in updated_nc12s if len(nc.sales_history) > 0]
        total_sales_records = sum(len(nc.sales_history) for nc in updated_nc12s)

        # Performance metrics
        throughput = len(pd.DataFrame(ymbd_df)) / (parse_time / 1000) if parse_time > 0 else 0

        print(f"\n✓ YMBD data parsed successfully")
        print(f"  - Parse time: {parse_time:.2f} ms")
        print(f"  - 12NCs updated: {len(nc12s_with_sales)}/{len(nc12s)}")
        print(f"  - Total sales records: {total_sales_records:,}")
        if nc12s_with_sales:
            print(f"  - Avg records per 12NC: {total_sales_records/len(nc12s_with_sales):.1f}")
        print(f"  - Throughput: {throughput:.2f} rows/sec")

        # Coverage analysis
        coverage = (len(nc12s_with_sales) / len(nc12s) * 100) if nc12s else 0
        print(f"\n📊 Coverage Analysis:")
        print(f"  - Match rate: {coverage:.1f}%")
        print(f"  - Matched: {len(nc12s_with_sales)}")
        print(f"  - Unmatched: {len(nc12s) - len(nc12s_with_sales)}")

        # Sample sales data
        if nc12s_with_sales:
            print(f"\n💰 Sample Sales Data:")
            sample = nc12s_with_sales[0]
            print(f"  - 12NC: {sample.id}")
            print(f"  - Sales records: {len(sample.sales_history)}")
            if sample.sales_history:
                sr = sample.sales_history[0]
                print(f"    └─ Date: {sr.date}, Qty: {sr.quantity}")

            # Validate sales records
            for nc in nc12s_with_sales[:5]:  # Check first 5
                for record in nc.sales_history:
                    assert isinstance(record, SalesRecord), "Should be SalesRecord object"
                    assert hasattr(record, "date"), "Record should have date"
                    assert hasattr(record, "quantity"), "Record should have quantity"
                    assert (
                        record.quantity > 0
                    ), f"Quantity should be positive, got {record.quantity}"

        print("\n" + "=" * 80)

    def test_parse_fit_cvi_to_sales_records(self, cbom_file, fit_file, config):
        """Test FIT/CVI parsing to SalesRecord objects"""
        if not cbom_file or not fit_file:
            pytest.skip("Need both CBOM and FIT/CVI files")

        print("\n" + "=" * 80)
        print("🧪 TEST: FIT/CVI Sales Record Parsing")
        print("=" * 80)

        # Setup: Load and transform CBOM first
        print("\n📥 Setup: Loading CBOM...")
        room_data, data_12nc = load_cbom(cbom_file, config)
        rooms, nc12s = transform_cbom_data(room_data, data_12nc, config)
        print(f"  ✓ Created {len(rooms)} room objects")

        # Load FIT/CVI data
        print("\n📥 Loading FIT/CVI...")
        fit_df = read_file(fit_file, "fit_cvi", header=0)
        print(f"  ✓ Loaded {len(pd.DataFrame(fit_df))} FIT/CVI rows")

        # Parse FIT/CVI
        print("\n🔄 Parsing FIT/CVI to sales records...")
        start_time = time.perf_counter()

        sales_records = parse_fit_cvi_to_sales_records(rooms, fit_df)

        end_time = time.perf_counter()
        parse_time = (end_time - start_time) * 1000

        # Assertions
        assert sales_records is not None, "Should not return None"
        assert isinstance(sales_records, list), "Should return a list"
        assert all(
            isinstance(sr, SalesRecord) for sr in sales_records
        ), "All items should be SalesRecord objects"

        # Performance metrics
        throughput = len(pd.DataFrame(fit_df)) / (parse_time / 1000) if parse_time > 0 else 0

        print(f"\n✓ FIT/CVI data parsed successfully")
        print(f"  - Parse time: {parse_time:.2f} ms")
        print(f"  - Sales records created: {len(sales_records):,}")
        print(f"  - Throughput: {throughput:.2f} rows/sec")

        # Data summary
        if sales_records:
            total_qty = sum(sr.quantity for sr in sales_records)
            unique_rooms = len(set(sr.identifier for sr in sales_records))
            unique_dates = len(set(sr.date for sr in sales_records))

            print(f"\n📊 Data Summary:")
            print(f"  - Total quantity: {total_qty:,}")
            print(f"  - Unique rooms: {unique_rooms}")
            print(f"  - Unique dates: {unique_dates}")
            print(f"  - Avg qty/record: {total_qty/len(sales_records):.1f}")

            print(f"\n💰 Sample Sales Record:")
            sr = sales_records[0]
            print(f"  - Room: {sr.identifier}")
            print(f"  - Date: {sr.date}")
            print(f"  - Quantity: {sr.quantity}")

            # Validate
            for record in sales_records[:10]:  # Check first 10
                assert hasattr(record, "identifier"), "Record should have identifier"
                assert hasattr(record, "date"), "Record should have date"
                assert hasattr(record, "quantity"), "Record should have quantity"
                assert record.quantity > 0, f"Quantity should be positive, got {record.quantity}"

        print("\n" + "=" * 80)


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestIntegration:
    """End-to-end integration tests"""

    def test_complete_pipeline(self, cbom_file, ymbd_file, fit_file, config):
        """Test complete data loading and transformation pipeline"""
        if not cbom_file:
            pytest.skip("Need CBOM file for integration test")

        print("\n" + "=" * 80)
        print("🧪 INTEGRATION TEST: Complete Data Pipeline")
        print("=" * 80)

        start_time = time.perf_counter()

        # Step 1: Load and transform CBOM
        print("\n1️⃣  Loading and transforming CBOM...")
        room_data, data_12nc = load_cbom(cbom_file, config)
        rooms, nc12s = transform_cbom_data(room_data, data_12nc, config)
        print(f"   ✓ Created {len(rooms)} rooms and {len(nc12s)} 12NCs")

        # Step 2: Load and process YMBD (if available)
        ymbd_coverage = 0
        if ymbd_file:
            print("\n2️⃣  Loading and processing YMBD...")
            ymbd_df = read_file(ymbd_file, "ymbd", header=0)
            nc12s = parse_ymbd_to_sales_records(nc12s, ymbd_df)
            ymbd_coverage = sum(1 for nc in nc12s if len(nc.sales_history) > 0)
            print(f"   ✓ Updated {ymbd_coverage}/{len(nc12s)} 12NCs with sales data")
        else:
            print("\n2️⃣  Skipping YMBD (no file provided)")

        # Step 3: Load and process FIT/CVI (if available)
        fit_records = []
        if fit_file:
            print("\n3️⃣  Loading and processing FIT/CVI...")
            fit_df = read_file(fit_file, "fit_cvi", header=0)
            fit_records = parse_fit_cvi_to_sales_records(rooms, fit_df)
            print(f"   ✓ Created {len(fit_records)} FIT/CVI sales records")
        else:
            print("\n3️⃣  Skipping FIT/CVI (no file provided)")

        end_time = time.perf_counter()
        pipeline_time = (end_time - start_time) * 1000

        # Calculate totals
        total_sales_records = sum(len(nc.sales_history) for nc in nc12s) + len(fit_records)

        print(f"\n✅ PIPELINE COMPLETE")
        print(f"  - Total time: {pipeline_time:.2f} ms")
        print(f"  - Rooms: {len(rooms)}")
        print(f"  - 12NCs: {len(nc12s)}")
        print(f"  - Total sales records: {total_sales_records:,}")

        # Data consistency checks
        print(f"\n🔍 Data Consistency Checks:")

        # Check 1: All rooms have valid IDs
        rooms_valid = all(r.id for r in rooms)
        print(f"  {'✓' if rooms_valid else '✗'} All rooms have IDs")
        assert rooms_valid, "All rooms should have IDs"

        # Check 2: All 12NCs have valid IDs
        nc12s_valid = all(nc.id and len(nc.id) == 12 and nc.id.isdigit() for nc in nc12s)
        print(f"  {'✓' if nc12s_valid else '✗'} All 12NCs have valid 12-digit IDs")
        assert nc12s_valid, "All 12NCs should have valid IDs"

        # Check 3: All sales records have valid dates
        if ymbd_coverage > 0:
            sales_dates_valid = True
            for nc in nc12s:
                for record in nc.sales_history:
                    if not hasattr(record, "date") or record.date is None:
                        sales_dates_valid = False
                        break
                if not sales_dates_valid:
                    break
            print(f"  {'✓' if sales_dates_valid else '✗'} All YMBD sales records have valid dates")
            assert sales_dates_valid, "All sales records should have valid dates"

        # Check 4: All sales records have positive quantities
        if ymbd_coverage > 0:
            quantities_valid = True
            for nc in nc12s:
                for record in nc.sales_history:
                    if record.quantity <= 0:
                        quantities_valid = False
                        break
                if not quantities_valid:
                    break
            print(f"  {'✓' if quantities_valid else '✗'} All sales quantities are positive")
            assert quantities_valid, "All sales quantities should be positive"

        print(f"\n🎉 All consistency checks passed!")
        print("\n" + "=" * 80)


# ============================================================================
# MAIN EXECUTION
# ============================================================================


if __name__ == "__main__":
    """Run tests standalone with file pickers"""
    print("\n")
    print("=" * 80)
    print("  INFRASTRUCTURE TEST SUITE - STANDALONE MODE")
    print("=" * 80)

    # Run pytest with captured output
    pytest.main(
        [
            __file__,
            "-v",  # Verbose
            "-s",  # No capture (show prints)
            "--tb=short",  # Short traceback
        ]
    )
