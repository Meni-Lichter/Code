"""
Infrastructure Test Suite for Room_12NC_PerformanceCenter
Tests data loading and transformation performance and accuracy.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
import pandas as pd
import time
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
    cbom_file = pick_file(
        "Select CBOM File", [("Excel files", "*.xlsx *.xlsm *.xls"), ("All files", "*.*")]
    )
    ymbd_file = pick_file(
        "Select YMBD File", [("Excel files", "*.xlsx *.xlsm *.xls"), ("All files", "*.*")]
    )
    fit_file = pick_file(
        "Select FIT/CVI File", [("Excel files", "*.xlsx *.xlsm *.xls"), ("All files", "*.*")]
    )
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

        start_time = time.perf_counter()
        room_data, data_12nc = load_cbom(cbom_file, config)
        load_time = (time.perf_counter() - start_time) * 1000

        assert room_data is not None, "room_data should not be None"
        assert data_12nc is not None, "data_12nc should not be None"
        assert isinstance(room_data, dict), "room_data should be a dictionary"
        assert isinstance(data_12nc, dict), "data_12nc should be a dictionary"
        assert len(room_data) > 0, "Should load at least one room"
        assert len(data_12nc) > 0, "Should load at least one 12NC"

        total_items = len(room_data) + len(data_12nc)
        throughput = total_items / (load_time / 1000) if load_time > 0 else 0

        print(f"CBOM File Loading:")
        print(f"  Load time: {load_time:.2f} ms")
        print(f"  Rooms: {len(room_data):,}")
        print(f"  12NCs: {len(data_12nc):,}")
        print(f"  Throughput: {throughput:.2f} items/sec")

    def test_load_ymbd(self, ymbd_file):
        """Test YMBD file loading performance"""
        if not ymbd_file:
            pytest.skip("No YMBD file provided")

        start_time = time.perf_counter()
        ymbd_df = read_file(ymbd_file, "ymbd", header=0)
        load_time = (time.perf_counter() - start_time) * 1000

        assert ymbd_df is not None, "DataFrame should not be None"
        assert isinstance(ymbd_df, pd.DataFrame), "Should return pandas DataFrame"
        assert len(ymbd_df) > 0, "DataFrame should not be empty"

        rows = len(ymbd_df)
        throughput = rows / (load_time / 1000) if load_time > 0 else 0

        print(f"YMBD File Loading:")
        print(f"  Load time: {load_time:.2f} ms")
        print(f"  Rows: {rows:,}")
        print(f"  Columns: {len(ymbd_df.columns)}")
        print(f"  Throughput: {throughput:.2f} rows/sec")

    def test_load_fit_cvi(self, fit_file):
        """Test FIT/CVI file loading performance"""
        if not fit_file:
            pytest.skip("No FIT/CVI file provided")

        start_time = time.perf_counter()
        fit_df = read_file(fit_file, "fit_cvi", header=0)
        load_time = (time.perf_counter() - start_time) * 1000

        assert fit_df is not None, "DataFrame should not be None"
        assert isinstance(fit_df, pd.DataFrame), "Should return pandas DataFrame"
        assert len(fit_df) > 0, "DataFrame should not be empty"

        rows = len(fit_df)
        throughput = rows / (load_time / 1000) if load_time > 0 else 0

        print(f"FIT/CVI File Loading:")
        print(f"  Load time: {load_time:.2f} ms")
        print(f"  Rows: {rows:,}")
        print(f"  Columns: {len(fit_df.columns)}")
        print(f"  Throughput: {throughput:.2f} rows/sec")


# ============================================================================
# DATA TRANSFORMER TESTS
# ============================================================================


class TestDataTransformers:
    """Test suite for data transformation functions"""

    def test_transform_cbom_data(self, cbom_file, config):
        """Test CBOM data transformation to Room and TwelveNC objects"""
        if not cbom_file:
            pytest.skip("No CBOM file provided")

        room_data, data_12nc = load_cbom(cbom_file, config)
        start_time = time.perf_counter()
        rooms, nc12s = transform_cbom_data(room_data, data_12nc, config)
        transform_time = (time.perf_counter() - start_time) * 1000

        # Validation
        assert rooms and nc12s, "Should create rooms and 12NCs"
        assert all(isinstance(r, Room) for r in rooms), "All should be Room objects"
        assert all(isinstance(nc, TwelveNC) for nc in nc12s), "All should be TwelveNC objects"
        assert all(r.id for r in rooms), "All rooms should have IDs"
        assert all(
            nc.id and len(nc.id) == 12 for nc in nc12s
        ), "All 12NCs should have valid 12-digit IDs"

        print(f"CBOM Data Transformation:")
        print(f"  Transform time: {transform_time:.2f} ms")
        print(f"  Room objects: {len(rooms)}")
        print(f"  TwelveNC objects: {len(nc12s)}")
        print(
            f"  Throughput: {(len(rooms) + len(nc12s)) / (transform_time / 1000):.2f} objects/sec"
        )

        r = rooms[0]
        print(f"\n  Sample Room - {r.id}:")
        print(f"    Components: {len(r.twelve_ncs)} | Items: {r.total_items}")
        for idx, (nc_id, qty) in enumerate(list(r.twelve_ncs.items())[:3]):
            print(f"      {nc_id}: Qty {qty}")
        if len(r.twelve_ncs) > 3:
            print(f"      ... and {len(r.twelve_ncs) - 3} more")

        nc = nc12s[0]
        print(f"\n  Sample 12NC - {nc.id}:")
        print(f"    Rooms: {len(nc.rooms)} | Items: {nc.total_items}")
        for idx, (room_id, qty) in enumerate(list(nc.rooms.items())[:3]):
            print(f"      {room_id}: Qty {qty}")
        if len(nc.rooms) > 3:
            print(f"      ... and {len(nc.rooms) - 3} more")

    def test_parse_ymbd_to_sales_records(self, cbom_file, ymbd_file, config):
        """Test YMBD parsing and linking to TwelveNC objects"""
        if not cbom_file or not ymbd_file:
            pytest.skip("Need both CBOM and YMBD files")

        room_data, data_12nc = load_cbom(cbom_file, config)
        rooms, nc12s = transform_cbom_data(room_data, data_12nc, config)
        ymbd_df = read_file(ymbd_file, "ymbd", header=0)
        start_time = time.perf_counter()
        updated_nc12s = parse_ymbd_to_sales_records(nc12s, ymbd_df)
        parse_time = (time.perf_counter() - start_time) * 1000

        # Assertions
        assert updated_nc12s is not None, "Should not return None"
        assert len(updated_nc12s) == len(nc12s), "Should return same number of 12NCs"

        nc12s_with_sales = [nc for nc in updated_nc12s if len(nc.sales_history) > 0]
        total_sales = sum(len(nc.sales_history) for nc in updated_nc12s)
        coverage = (len(nc12s_with_sales) / len(nc12s) * 100) if nc12s else 0

        print(f"YMBD Sales Record Parsing:")
        print(f"  Parse time: {parse_time:.2f} ms")
        print(f"  12NCs updated: {len(nc12s_with_sales)}/{len(nc12s)} ({coverage:.1f}%)")
        print(f"  Total sales records: {total_sales:,}")
        if nc12s_with_sales:
            print(f"  Avg records per 12NC: {total_sales/len(nc12s_with_sales):.1f}")
        print(f"  Throughput: {len(pd.DataFrame(ymbd_df)) / (parse_time / 1000):.2f} rows/sec")

        if nc12s_with_sales:
            sample = nc12s_with_sales[0]
            print(f"\n  Sample 12NC - {sample.id}:")
            print(f"    Rooms: {len(sample.rooms)} | Sales records: {len(sample.sales_history)}")
            for idx, (room_id, qty) in enumerate(list(sample.rooms.items())[:3]):
                print(f"      {room_id}: Qty {qty}")
            if len(sample.rooms) > 3:
                print(f"      ... and {len(sample.rooms) - 3} more")
            print(f"    Recent sales:")
            for idx, sr in enumerate(sample.sales_history[:3]):
                print(f"      {sr.date}: Qty {sr.quantity}")
            if len(sample.sales_history) > 3:
                print(f"      ... and {len(sample.sales_history) - 3} more records")

            # Validate first 5
            for nc in nc12s_with_sales[:5]:
                for record in nc.sales_history:
                    assert isinstance(record, SalesRecord), "Should be SalesRecord object"
                    assert hasattr(record, "date") and record.date, "Should have date"
                    assert (
                        hasattr(record, "quantity") and record.quantity > 0
                    ), "Should have positive quantity"

        print("\n" + "=" * 80)

    def test_parse_fit_cvi_to_sales_records(self, cbom_file, fit_file, config):
        """Test FIT/CVI parsing and linking to Room objects"""
        if not cbom_file or not fit_file:
            pytest.skip("Need both CBOM and FIT/CVI files")

        room_data, data_12nc = load_cbom(cbom_file, config)
        rooms, nc12s = transform_cbom_data(room_data, data_12nc, config)
        fit_df = read_file(fit_file, "fit_cvi", header=0)
        start_time = time.perf_counter()
        updated_rooms = parse_fit_cvi_to_sales_records(rooms, fit_df)
        parse_time = (time.perf_counter() - start_time) * 1000

        # Assertions
        assert updated_rooms is not None, "Should not return None"
        assert len(updated_rooms) == len(rooms), "Should return same number of rooms"
        assert all(
            isinstance(room, Room) for room in updated_rooms
        ), "All items should be Room objects"

        # Extract all sales records from rooms
        all_sales_records = []
        for room in updated_rooms:
            all_sales_records.extend(room.sales_history)

        rooms_with_sales = [r for r in updated_rooms if len(r.sales_history) > 0]
        throughput = len(pd.DataFrame(fit_df)) / (parse_time / 1000) if parse_time > 0 else 0

        print(f"FIT/CVI Sales Record Parsing:")
        print(f"  Parse time: {parse_time:.2f} ms")
        print(f"  Rooms updated: {len(rooms_with_sales)}/{len(updated_rooms)}")
        print(f"  Total sales records: {len(all_sales_records):,}")
        print(f"  Throughput: {throughput:.2f} rows/sec")

        if all_sales_records:
            assert all(
                isinstance(sr, SalesRecord) for sr in all_sales_records
            ), "All should be SalesRecord objects"
            assert all(
                hasattr(sr, "date") and sr.date for sr in all_sales_records[:10]
            ), "Records should have dates"
            assert all(
                sr.quantity > 0 for sr in all_sales_records[:10]
            ), "Quantities should be positive"

            if rooms_with_sales:
                sample_room = rooms_with_sales[0]
                print(f"\n  Sample Room - {sample_room.id}:")
                print(
                    f"    Components: {len(sample_room.twelve_ncs)} | Sales records: {len(sample_room.sales_history)}"
                )
                for idx, (nc_id, qty) in enumerate(list(sample_room.twelve_ncs.items())[:3]):
                    print(f"      {nc_id}: Qty {qty}")
                if len(sample_room.twelve_ncs) > 3:
                    print(f"      ... and {len(sample_room.twelve_ncs) - 3} more")
                print(f"    Recent sales:")
                for idx, sr in enumerate(sample_room.sales_history[:3]):
                    print(f"      {sr.date}: Qty {sr.quantity}")
                if len(sample_room.sales_history) > 3:
                    print(f"      ... and {len(sample_room.sales_history) - 3} more records")


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestIntegration:
    """End-to-end integration tests"""

    def test_complete_pipeline(self, cbom_file, ymbd_file, fit_file, config):
        """Test complete data loading and transformation pipeline"""
        if not cbom_file:
            pytest.skip("Need CBOM file for integration test")

        start_time = time.perf_counter()
        room_data, data_12nc = load_cbom(cbom_file, config)
        rooms, nc12s = transform_cbom_data(room_data, data_12nc, config)

        # Validate CBOM objects
        assert all(isinstance(r, Room) for r in rooms), "All rooms should be Room objects"
        assert all(isinstance(nc, TwelveNC) for nc in nc12s), "All 12NCs should be TwelveNC objects"
        assert all(r.id for r in rooms), "All rooms should have IDs"

        ymbd_coverage = 0
        if ymbd_file:
            ymbd_df = read_file(ymbd_file, "ymbd", header=0)
            nc12s = parse_ymbd_to_sales_records(nc12s, ymbd_df)
            ymbd_coverage = sum(1 for nc in nc12s if len(nc.sales_history) > 0)

            # Validate YMBD data
            if ymbd_coverage > 0:
                all_ymbd_records = [sr for nc in nc12s for sr in nc.sales_history]
                assert all(
                    isinstance(sr, SalesRecord) for sr in all_ymbd_records
                ), "All should be SalesRecord objects"
                assert all(
                    hasattr(sr, "date") and sr.date for sr in all_ymbd_records
                ), "All should have dates"
                assert all(
                    sr.quantity > 0 for sr in all_ymbd_records
                ), "All quantities should be positive"
        fit_coverage = 0
        if fit_file:
            fit_df = read_file(fit_file, "fit_cvi", header=0)
            rooms = parse_fit_cvi_to_sales_records(rooms, fit_df)
            fit_coverage = sum(1 for r in rooms if len(r.sales_history) > 0)
            all_fit_records = [sr for r in rooms for sr in r.sales_history]

            # Validate FIT/CVI data
            if all_fit_records:
                assert all(
                    isinstance(sr, SalesRecord) for sr in all_fit_records
                ), "All should be SalesRecord objects"
                assert all(
                    hasattr(sr, "date") and sr.date for sr in all_fit_records
                ), "All should have dates"
                assert all(
                    sr.quantity > 0 for sr in all_fit_records
                ), "All quantities should be positive"
        end_time = time.perf_counter()
        pipeline_time = (end_time - start_time) * 1000

        # Calculate totals
        total_ymbd_records = sum(len(nc.sales_history) for nc in nc12s)
        total_fit_records = sum(len(r.sales_history) for r in rooms)
        total_sales_records = total_ymbd_records + total_fit_records

        print(f"Complete Pipeline:")
        print(f"  Total time: {pipeline_time:.2f} ms")
        print(f"  Rooms: {len(rooms)}")
        print(f"  12NCs: {len(nc12s)}")
        print(f"  YMBD sales records: {total_ymbd_records:,}")
        print(f"  FIT/CVI sales records: {total_fit_records:,}")
        print(f"  Total sales records: {total_sales_records:,}")

        invalid_rooms = [r for r in rooms if not r.id or not isinstance(r, Room)]
        assert not invalid_rooms, f"Found {len(invalid_rooms)} invalid rooms"

        invalid_12ncs = [
            nc for nc in nc12s if not nc.id or len(nc.id) != 12 or not isinstance(nc, TwelveNC)
        ]
        assert not invalid_12ncs, f"Found {len(invalid_12ncs)} invalid 12NCs"

        print(f"\n  All rooms valid: {len(rooms) - len(invalid_rooms)}/{len(rooms)}")
        print(f"  All 12NCs valid: {len(nc12s) - len(invalid_12ncs)}/{len(nc12s)}")

        if ymbd_coverage > 0:
            print(
                f"  YMBD coverage: {ymbd_coverage}/{len(nc12s)} 12NCs ({ymbd_coverage/len(nc12s)*100:.1f}%)"
            )

        if fit_coverage > 0:
            print(
                f"  FIT/CVI coverage: {fit_coverage}/{len(rooms)} rooms ({fit_coverage/len(rooms)*100:.1f}%)"
            )


# ============================================================================
# MAIN EXECUTION
# ============================================================================


if __name__ == "__main__":
    """Run tests standalone with file pickers"""
    pytest.main(
        [
            __file__,
            "-v",  # Verbose
            "-s",  # No capture (show prints)
            "--tb=short",  # Short traceback
        ]
    )
