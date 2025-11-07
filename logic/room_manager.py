"""
Room management for multi-user voting sessions.

Handles room creation, joining, and shared state management.
"""

import random
import string
from datetime import datetime
from typing import Dict, Optional, List
from dataclasses import dataclass, field


@dataclass
class RoomState:
    """Represents the state of a voting room."""
    
    room_id: str
    available_options: List[str] = field(default_factory=list)
    selected_positions: Dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    participant_count: int = 0
    
    def update_positions(self, positions: Dict[str, float]) -> None:
        """Update the positions for selected options."""
        self.selected_positions = positions.copy()
        self.last_updated = datetime.now()
    
    def update_options(self, options: List[str]) -> None:
        """Update the list of available options."""
        self.available_options = options.copy()
        self.last_updated = datetime.now()


class RoomManager:
    """Manages voting rooms with in-memory storage."""
    
    def __init__(self):
        """Initialize the room manager."""
        self._rooms: Dict[str, RoomState] = {}
    
    def generate_room_code(self, length: int = 6) -> str:
        """Generate a unique room code."""
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
            if code not in self._rooms:
                return code
    
    def create_room(self, initial_options: Optional[List[str]] = None) -> str:
        """
        Create a new room and return its code.
        
        Args:
            initial_options: Optional list of initial voting options
            
        Returns:
            The generated room code
        """
        room_code = self.generate_room_code()
        
        if initial_options is None:
            initial_options = ['Option A', 'Option B', 'Option C', 'Option D']
        
        self._rooms[room_code] = RoomState(
            room_id=room_code,
            available_options=initial_options,
            participant_count=1
        )
        
        return room_code
    
    def join_room(self, room_code: str) -> Optional[RoomState]:
        """
        Join an existing room.
        
        Args:
            room_code: The room code to join
            
        Returns:
            The room state if room exists, None otherwise
        """
        room_code = room_code.upper().strip()
        
        if room_code in self._rooms:
            self._rooms[room_code].participant_count += 1
            return self._rooms[room_code]
        
        return None
    
    def get_room(self, room_code: str) -> Optional[RoomState]:
        """
        Get the current state of a room.
        
        Args:
            room_code: The room code
            
        Returns:
            The room state if room exists, None otherwise
        """
        return self._rooms.get(room_code.upper().strip())
    
    def update_room_options(self, room_code: str, options: List[str]) -> bool:
        """
        Update the available options in a room.
        
        Args:
            room_code: The room code
            options: The new list of options
            
        Returns:
            True if successful, False if room doesn't exist
        """
        room = self.get_room(room_code)
        if room:
            room.update_options(options)
            return True
        return False
    
    def update_room_positions(self, room_code: str, positions: Dict[str, float]) -> bool:
        """
        Update the positions in a room.
        
        Args:
            room_code: The room code
            positions: Dictionary of option names to positions
            
        Returns:
            True if successful, False if room doesn't exist
        """
        room = self.get_room(room_code)
        if room:
            room.update_positions(positions)
            return True
        return False
    
    def room_exists(self, room_code: str) -> bool:
        """Check if a room exists."""
        return room_code.upper().strip() in self._rooms
    
    def get_room_count(self) -> int:
        """Get the total number of active rooms."""
        return len(self._rooms)
    
    def cleanup_old_rooms(self, max_age_hours: int = 24) -> int:
        """
        Remove rooms older than specified hours.
        
        Args:
            max_age_hours: Maximum age in hours before cleanup
            
        Returns:
            Number of rooms cleaned up
        """
        from datetime import timedelta
        
        now = datetime.now()
        rooms_to_remove = []
        
        for room_code, room in self._rooms.items():
            age = now - room.last_updated
            if age > timedelta(hours=max_age_hours):
                rooms_to_remove.append(room_code)
        
        for room_code in rooms_to_remove:
            del self._rooms[room_code]
        
        return len(rooms_to_remove)


# Global singleton instance
_room_manager_instance: Optional[RoomManager] = None


def get_room_manager() -> RoomManager:
    """Get or create the global room manager instance."""
    global _room_manager_instance
    
    if _room_manager_instance is None:
        _room_manager_instance = RoomManager()
    
    return _room_manager_instance
