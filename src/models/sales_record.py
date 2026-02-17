# Data class for individual sales records in the Room-12NC Performance Center application
from dataclasses import dataclass
from datetime import date

@dataclass
class SalesRecord:
    """Individual sales transaction"""
    twelve_nc: str
    room: str
    quantity: int
    date: date
    
    def __post_init__(self):
        """Validate data on initialization"""
        if self.quantity < 0:
            raise ValueError("Quantity cannot be negative")
        if not self.twelve_nc:
            raise ValueError("12NC cannot be empty")
        if not self.room:
            raise ValueError("Room cannot be empty")