"""File utility functions for file locking and output path computation"""
import os
from pathlib import Path
from datetime import datetime


# --- File locking check - mechanism 
def file_in_use(path) -> bool:
    """
    Returns True if the file appears to be locked/open by another process.
    Uses advisory locks where available; falls back to PermissionError.
    """
    if not os.path.isfile(path): 
        return True
    try:
        # Open read+binary to probe lock status
        with open(path, "rb+") as f:
            if os.name == "nt":
                import msvcrt
                try:
                    msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
                    msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
                except OSError:
                    return True
        return False
    except PermissionError:
        return True
    except Exception:
        # If anything odd happens, be conservative
        return True
    


def ensure_file_not_open(path: Path, label: str) :
    """
    Raise PermissionError if the file appears to be open/locked.
    """
    locked = file_in_use(path)
    if locked:
        raise PermissionError(
            f"The following {label} file looks open/locked:\n- " +
            f"{path.name}\n\nClose it and try again."
        )
    


def compute_output_path(leading_path: Path) -> Path:
    """
    Compute output path for enriched report in the LEADING file's grandparent folder,
    in a subfolder "IB_MatchWise_Results". The filename includes a timestamp.
    """
    MAX_PATH = 260  # Windows path limit
    MIN_FILENAME_LENGTH = 20  # Ensure meaningful filename

    ts = datetime.now().strftime("%m-%d-%Y__%H-%M-%S")
    
    # Validate input path depth
    try:
        leading_parent = leading_path.parent.parent
    except (AttributeError, IndexError):
        # Fallback to parent if grandparent doesn't exist
        leading_parent = leading_path.parent

    # Build directory name with length checking
    res_folder_name = f"IB_MatchWise_Results__{ts}"
    base_filename = f"Results_Report__{ts}.xlsx"
    
    # Calculate available space for directory name
    base_path_len = len(str(leading_parent))
    remaining_space = MAX_PATH - base_path_len - len(base_filename) - 10  # buffer
    
    if len(res_folder_name) > remaining_space:
        # Shorten directory name intelligently
        res_folder_name = f"IB_Results__{ts}"
        if len(res_folder_name) > remaining_space:
            # Last resort: minimal directory name
            res_folder_name = f"IB__{ts}"

    out_dir = leading_parent / res_folder_name
    
    # Create directory with unique naming if conflict
    counter = 1
    original_dir = out_dir
    while out_dir.exists():
        out_dir = original_dir.parent / f"{original_dir.name}_{counter}"
        counter += 1
        if counter > 100:  # Prevent infinite loop
            break
    
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Build final path with validation
    final_path = out_dir / base_filename
    
    # Final length check
    if len(str(final_path)) > MAX_PATH:
        # Shorten filename while preserving extension
        available_for_name = MAX_PATH - len(str(out_dir)) - 6  # .xlsx + separator
        if available_for_name < MIN_FILENAME_LENGTH:
            # Directory path too long, use very short name
            final_filename = "report.xlsx"
        else:
            # Keep timestamp but shorten description
            short_name = f"Report_{ts}.xlsx"
            if len(short_name) > available_for_name:
                # Use minimal name with just date
                date_only = ts.split("__")[0]
                short_name = f"R_{date_only}.xlsx"
            final_filename = short_name
        
        final_path = out_dir / final_filename
    
    return final_path
