"""
Persistence layer for room data using JSON storage.

Provides simple file-based storage for room states with automatic
serialization and deserialization.
"""

import json
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
from .room_manager import RoomState


class RoomPersistence:
    """Handles saving and loading room data to/from JSON files."""
    
    def __init__(self, data_dir: str = "data/rooms"):
        """
        Initialize the persistence layer.
        
        Args:
            data_dir: Directory to store room data files
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.rooms_file = self.data_dir / "rooms.json"
    
    def save_rooms(self, rooms: Dict[str, RoomState]) -> bool:
        """
        Save all rooms to JSON file.
        
        Args:
            rooms: Dictionary of room_code -> RoomState
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert rooms to serializable format
            rooms_data = {}
            for room_code, room in rooms.items():
                rooms_data[room_code] = {
                    'room_id': room.room_id,
                    'available_options': room.available_options,
                    'participant_votes': room.participant_votes,
                    'created_at': room.created_at.isoformat(),
                    'last_updated': room.last_updated.isoformat(),
                    'participant_count': room.participant_count
                }
            
            # Write to file with atomic write (write to temp, then rename)
            temp_file = self.rooms_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(rooms_data, f, indent=2, ensure_ascii=False)
            
            # Atomic rename
            temp_file.replace(self.rooms_file)
            return True
            
        except Exception as e:
            print(f"Error saving rooms: {e}")
            return False
    
    def load_rooms(self) -> Dict[str, RoomState]:
        """
        Load all rooms from JSON file.
        
        Returns:
            Dictionary of room_code -> RoomState
        """
        if not self.rooms_file.exists():
            return {}
        
        try:
            with open(self.rooms_file, 'r', encoding='utf-8') as f:
                rooms_data = json.load(f)
            
            # Convert back to RoomState objects
            rooms = {}
            for room_code, data in rooms_data.items():
                # Handle both old format (selected_positions) and new format (participant_votes)
                participant_votes = data.get('participant_votes', {})
                
                # Migrate old format if needed
                if 'selected_positions' in data and data['selected_positions'] and not participant_votes:
                    participant_votes = {'legacy_participant': data['selected_positions']}
                
                room = RoomState(
                    room_id=data['room_id'],
                    available_options=data['available_options'],
                    participant_votes=participant_votes,
                    created_at=datetime.fromisoformat(data['created_at']),
                    last_updated=datetime.fromisoformat(data['last_updated']),
                    participant_count=data.get('participant_count', len(participant_votes))
                )
                rooms[room_code] = room
            
            return rooms
            
        except Exception as e:
            print(f"Error loading rooms: {e}")
            return {}
    
    def delete_room(self, room_code: str) -> bool:
        """
        Delete a specific room from storage.
        
        Args:
            room_code: The room code to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            rooms = self.load_rooms()
            
            if room_code in rooms:
                del rooms[room_code]
                return self.save_rooms(rooms)
            
            return False
            
        except Exception as e:
            print(f"Error deleting room: {e}")
            return False
    
    def clear_all(self) -> bool:
        """
        Clear all room data (useful for testing).
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.rooms_file.exists():
                self.rooms_file.unlink()
            return True
        except Exception as e:
            print(f"Error clearing rooms: {e}")
            return False
    
    def get_storage_size(self) -> int:
        """
        Get the size of the storage file in bytes.
        
        Returns:
            Size in bytes, or 0 if file doesn't exist
        """
        if self.rooms_file.exists():
            return self.rooms_file.stat().st_size
        return 0
    
    def backup_rooms(self, backup_name: Optional[str] = None) -> bool:
        """
        Create a backup of the current rooms file.
        
        Args:
            backup_name: Optional backup file name (defaults to timestamp)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.rooms_file.exists():
            return False
        
        try:
            if backup_name is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"rooms_backup_{timestamp}.json"
            
            backup_path = self.data_dir / backup_name
            
            # Copy the file
            import shutil
            shutil.copy2(self.rooms_file, backup_path)
            return True
            
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False
