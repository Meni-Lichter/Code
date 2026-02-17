from dataclasses import dataclass
from typing import Dict

@dataclass
class Room12NCMapping:
    """Mapping between rooms and 12NCs"""
    room: str
    twelve_ncs: Dict[str, int]  # {12NC: quantity}
    
    @property
    def total_items(self) -> int:
        """Total number of items in room"""
        return sum(self.twelve_ncs.values())
    
    def has_12nc(self, twelve_nc: str) -> bool:
        """Check if room contains specific 12NC"""
        return twelve_nc in self.twelve_ncs