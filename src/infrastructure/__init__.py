"""Infrastructure layer - data loading and external system interactions"""

from .data_loaders import load_cbom, read_file

__all__ = [
    'load_cbom',
    'read_file',
]
