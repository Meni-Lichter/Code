from dataclasses import dataclass
from typing import Dict

@dataclass
class Room12NCMap:
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
    def show_12ncs(self) -> str:
        print (f"Room: {self.room} contains the following 12NCs:")
        for nc, qty in self.twelve_ncs.items():
            print(f"12NC: {nc}, Quantity: {qty}")
    

@dataclass
class TwelveNCRoomMap:
    """Mapping between 12NCs and rooms"""
    twelve_nc: str
    rooms: Dict[str, int]  # {room: quantity}
    
    @property
    def total_items(self) -> int:
        """Total number of items for 12NC"""
        return sum(self.rooms.values())
    
    def has_room(self, room: str) -> bool:
        """Check if 12NC is in specific room"""
        return room in self.rooms
    
    def show_rooms(self) -> str:
        print (f"12NC: {self.twelve_nc} is found in the following rooms:")
        for room, qty in self.rooms.items():
            print(f"Room: {room}, Quantity: {qty}")
        