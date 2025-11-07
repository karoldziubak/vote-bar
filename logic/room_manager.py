"""
Room management for multi-user voting sessions.

Handles room creation, joining, and shared state management.
Uses SQLite database for persistence.
"""

import random
import string
from datetime import datetime
from typing import Dict, Optional, List
from dataclasses import dataclass, field

from .database import get_database


@dataclass
class RoomState:
    """Represents the state of a voting room (in-memory representation)."""
    
    room_id: str
    available_options: List[str] = field(default_factory=list)
    participant_votes: Dict[str, Dict[str, float]] = field(default_factory=dict)  # participant_id -> {option: position}
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    
    @property
    def participant_count(self) -> int:
        """Get the number of participants who have voted."""
        return len(self.participant_votes)
    
    def submit_vote(self, participant_id: str, positions: Dict[str, float]) -> None:
        """Submit a vote from a participant."""
        self.participant_votes[participant_id] = positions.copy()
        self.last_updated = datetime.now()
    
    def get_aggregated_results(self) -> Dict[str, float]:
        """
        Aggregate all participant votes to calculate total points for each option.
        Each participant's vote is weighted equally.
        Returns dict of {option: total_points}
        """
        if not self.participant_votes:
            return {}
        
        # Count votes for each option
        option_points: Dict[str, float] = {}
        
        for participant_id, positions in self.participant_votes.items():
            # Calculate vote shares for this participant using Voronoi logic
            from logic.vote_logic import VoteResult
            vote_result = VoteResult(positions)
            
            # Add this participant's share to the total
            for option, share in vote_result.shares.items():
                if option not in option_points:
                    option_points[option] = 0.0
                option_points[option] += share
        
        return option_points
    
    def update_options(self, options: List[str]) -> None:
        """Update the list of available options."""
        self.available_options = options.copy()
        self.last_updated = datetime.now()


class RoomManager:
    """Manages voting rooms using SQLite database for persistence."""
    
    def __init__(self, db_path: str = "data/vote_bar.db"):
        """
        Initialize the room manager with database backend.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db = get_database(db_path)
        
        # Automatically clean up old rooms on startup
        cleaned = self.cleanup_old_rooms(max_age_hours=24)
        if cleaned > 0:
            print(f"Cleaned up {cleaned} expired room(s) on startup")
    
    def generate_room_code(self, length: int = 6) -> str:
        """Generate a unique room code."""
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
            if not self.db.room_exists(code):
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
        
        self.db.create_room(room_code, initial_options)
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
        room_data = self.db.get_room(room_code)
        
        if room_data:
            return RoomState(
                room_id=room_data['room_code'],
                available_options=room_data['available_options'],
                participant_votes=room_data['participant_votes'],
                created_at=room_data['created_at'],
                last_updated=room_data['last_updated']
            )
        
        return None
    
    def get_room(self, room_code: str) -> Optional[RoomState]:
        """
        Get the current state of a room.
        
        Args:
            room_code: The room code
            
        Returns:
            The room state if room exists, None otherwise
        """
        room_code = room_code.upper().strip()
        room_data = self.db.get_room(room_code)
        
        if room_data:
            return RoomState(
                room_id=room_data['room_code'],
                available_options=room_data['available_options'],
                participant_votes=room_data['participant_votes'],
                created_at=room_data['created_at'],
                last_updated=room_data['last_updated']
            )
        
        return None
    
    def update_room_options(self, room_code: str, options: List[str]) -> bool:
        """
        Update the available options in a room.
        
        Args:
            room_code: The room code
            options: The new list of options
            
        Returns:
            True if successful, False if room doesn't exist
        """
        room_code = room_code.upper().strip()
        return self.db.update_room_options(room_code, options)
    
    def update_room_positions(self, room_code: str, participant_id: str, positions: Dict[str, float]) -> bool:
        """
        Submit a vote from a participant to a room.
        
        Args:
            room_code: The room code
            participant_id: Unique identifier for the participant
            positions: Dictionary of option names to positions
            
        Returns:
            True if successful, False if room doesn't exist
        """
        room_code = room_code.upper().strip()
        return self.db.submit_vote(room_code, participant_id, positions)
    
    def room_exists(self, room_code: str) -> bool:
        """Check if a room exists."""
        return self.db.room_exists(room_code.upper().strip())
    
    def get_room_count(self) -> int:
        """Get the total number of active rooms."""
        all_rooms = self.db.get_all_rooms()
        return len(all_rooms)
    
    def cleanup_old_rooms(self, max_age_hours: int = 24) -> int:
        """
        Remove rooms older than specified hours.
        
        Args:
            max_age_hours: Maximum age in hours before cleanup
            
        Returns:
            Number of rooms cleaned up
        """
        return self.db.cleanup_old_rooms(hours=max_age_hours)


# Global singleton instance
_room_manager_instance: Optional[RoomManager] = None


def get_room_manager() -> RoomManager:
    """Get or create the global room manager instance."""
    global _room_manager_instance
    
    if _room_manager_instance is None:
        _room_manager_instance = RoomManager()
    
    return _room_manager_instance
