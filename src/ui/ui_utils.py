"""Shared UI utility functions"""

import customtkinter as ctk
from typing import Dict, Tuple


class FontCache:
    """Shared font cache to avoid recreating fonts repeatedly"""
    
    _cache: Dict[Tuple[str, int, str], ctk.CTkFont] = {}
    
    @classmethod
    def get_font(cls, family: str = "Segoe UI", size: int = 15, weight: str = "normal") -> ctk.CTkFont:
        """Get or create a cached font
        
        Args:
            family: Font family name
            size: Font size in points
            weight: Font weight ("normal" or "bold")
            
        Returns:
            CTkFont instance
        """
        # Type check for weight parameter
        font_weight = weight if weight in ["normal", "bold"] else "normal"
        
        key = (family, size, font_weight)
        if key not in cls._cache:
            cls._cache[key] = ctk.CTkFont(family=family, size=size, weight=font_weight)  # type: ignore
        return cls._cache[key]
    
    @classmethod
    def clear_cache(cls):
        """Clear the font cache (useful for testing or memory management)"""
        cls._cache.clear()
