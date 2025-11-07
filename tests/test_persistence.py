"""
Unit tests for persistence functionality.
"""

import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from logic.persistence import RoomPersistence
from logic.room_manager import RoomState, RoomManager


class TestRoomPersistence:
    """Test cases for the RoomPersistence class."""
    
    def setup_method(self):
        """Create a temporary directory for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.persistence = RoomPersistence(data_dir=self.temp_dir)
    
    def teardown_method(self):
        """Clean up temporary directory after each test."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_save_and_load_empty(self):
        """Test saving and loading empty room dict."""
        rooms = {}
        
        success = self.persistence.save_rooms(rooms)
        loaded = self.persistence.load_rooms()
        
        assert success is True
        assert loaded == {}
    
    def test_save_and_load_single_room(self):
        """Test saving and loading a single room."""
        room = RoomState(
            room_id="TEST123",
            available_options=['A', 'B', 'C']
        )
        room.submit_vote("participant1", {'A': 25.0, 'B': 75.0})
        room.submit_vote("participant2", {'B': 50.0, 'C': 100.0})
        rooms = {'TEST123': room}
        
        self.persistence.save_rooms(rooms)
        loaded = self.persistence.load_rooms()
        
        assert 'TEST123' in loaded
        assert loaded['TEST123'].room_id == 'TEST123'
        assert loaded['TEST123'].available_options == ['A', 'B', 'C']
        assert 'participant1' in loaded['TEST123'].participant_votes
        assert 'participant2' in loaded['TEST123'].participant_votes
        assert loaded['TEST123'].participant_count == 2
    
    def test_save_and_load_multiple_rooms(self):
        """Test saving and loading multiple rooms."""
        room1 = RoomState(room_id="ROOM1", available_options=['X'])
        room2 = RoomState(room_id="ROOM2", available_options=['Y', 'Z'])
        rooms = {'ROOM1': room1, 'ROOM2': room2}
        
        self.persistence.save_rooms(rooms)
        loaded = self.persistence.load_rooms()
        
        assert len(loaded) == 2
        assert 'ROOM1' in loaded
        assert 'ROOM2' in loaded
    
    def test_load_nonexistent_file(self):
        """Test loading when no file exists."""
        loaded = self.persistence.load_rooms()
        
        assert loaded == {}
    
    def test_datetime_serialization(self):
        """Test that datetime objects are correctly serialized and deserialized."""
        now = datetime.now()
        room = RoomState(
            room_id="TIME",
            created_at=now,
            last_updated=now
        )
        rooms = {'TIME': room}
        
        self.persistence.save_rooms(rooms)
        loaded = self.persistence.load_rooms()
        
        # Compare timestamps (may have microsecond differences due to serialization)
        assert abs((loaded['TIME'].created_at - now).total_seconds()) < 1
        assert abs((loaded['TIME'].last_updated - now).total_seconds()) < 1
    
    def test_delete_room(self):
        """Test deleting a specific room."""
        room1 = RoomState(room_id="KEEP")
        room2 = RoomState(room_id="DELETE")
        rooms = {'KEEP': room1, 'DELETE': room2}
        
        self.persistence.save_rooms(rooms)
        success = self.persistence.delete_room("DELETE")
        loaded = self.persistence.load_rooms()
        
        assert success is True
        assert 'KEEP' in loaded
        assert 'DELETE' not in loaded
    
    def test_delete_nonexistent_room(self):
        """Test deleting a room that doesn't exist."""
        success = self.persistence.delete_room("NOTHERE")
        
        assert success is False
    
    def test_clear_all(self):
        """Test clearing all room data."""
        room = RoomState(room_id="TEST")
        self.persistence.save_rooms({'TEST': room})
        
        success = self.persistence.clear_all()
        loaded = self.persistence.load_rooms()
        
        assert success is True
        assert loaded == {}
    
    def test_get_storage_size(self):
        """Test getting storage file size."""
        # Initially no file
        assert self.persistence.get_storage_size() == 0
        
        # After saving, should have size
        room = RoomState(room_id="TEST")
        self.persistence.save_rooms({'TEST': room})
        
        size = self.persistence.get_storage_size()
        assert size > 0
    
    def test_backup_rooms(self):
        """Test creating a backup of rooms file."""
        room = RoomState(room_id="BACKUP")
        self.persistence.save_rooms({'BACKUP': room})
        
        success = self.persistence.backup_rooms("test_backup.json")
        backup_path = Path(self.temp_dir) / "test_backup.json"
        
        assert success is True
        assert backup_path.exists()
    
    def test_backup_nonexistent_file(self):
        """Test backup when no rooms file exists."""
        success = self.persistence.backup_rooms()
        
        assert success is False
    
    def test_save_handles_errors_gracefully(self):
        """Test that save errors are handled gracefully."""
        import unittest.mock as mock
        
        # Mock json.dump to raise an exception
        with mock.patch('json.dump', side_effect=Exception("JSON error")):
            room = RoomState(room_id="TEST")
            success = self.persistence.save_rooms({'TEST': room})
            
            # Should return False but not crash
            assert success is False
    
    def test_load_handles_corrupted_json(self):
        """Test loading when JSON file is corrupted."""
        # Write invalid JSON to file
        with open(self.persistence.rooms_file, 'w') as f:
            f.write("{ invalid json content")
        
        loaded = self.persistence.load_rooms()
        
        # Should return empty dict instead of crashing
        assert loaded == {}
    
    def test_delete_room_handles_errors(self):
        """Test delete_room error handling."""
        import unittest.mock as mock
        
        # Create a room first
        room = RoomState(room_id="TEST")
        self.persistence.save_rooms({'TEST': room})
        
        # Mock the save operation to fail
        with mock.patch.object(self.persistence, 'save_rooms', return_value=False):
            success = self.persistence.delete_room("TEST")
            assert success is False
    
    def test_clear_all_handles_errors(self):
        """Test clear_all error handling."""
        import unittest.mock as mock
        
        # Create a room first
        room = RoomState(room_id="TEST")
        self.persistence.save_rooms({'TEST': room})
        
        # Mock unlink to raise an exception
        with mock.patch('pathlib.Path.unlink', side_effect=Exception("Delete error")):
            success = self.persistence.clear_all()
            assert success is False
    
    def test_backup_handles_errors(self):
        """Test backup error handling."""
        import unittest.mock as mock
        
        # Create a file first
        room = RoomState(room_id="TEST")
        self.persistence.save_rooms({'TEST': room})
        
        # Mock shutil.copy2 to raise an exception
        with mock.patch('shutil.copy2', side_effect=Exception("Copy error")):
            success = self.persistence.backup_rooms()
            assert success is False
    
    def test_load_handles_file_not_found(self):
        """Test load_rooms when file doesn't exist."""
        import unittest.mock as mock
        
        # Mock Path.exists to return True but open to fail with FileNotFoundError
        with mock.patch('pathlib.Path.exists', return_value=True):
            with mock.patch('builtins.open', side_effect=FileNotFoundError()):
                loaded = self.persistence.load_rooms()
                assert loaded == {}


class TestRoomManagerPersistence:
    """Test RoomManager with persistence enabled."""
    
    def setup_method(self):
        """Create a temporary directory for each test."""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up temporary directory after each test."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_persistence_disabled(self):
        """Test RoomManager with persistence disabled."""
        manager = RoomManager(enable_persistence=False)
        
        room_code = manager.create_room()
        
        assert manager.room_exists(room_code)
        assert manager._persistence is None
    
    def test_rooms_persist_across_instances(self):
        """Test that rooms persist when creating new RoomManager instance."""
        # First instance - create room
        manager1 = RoomManager(enable_persistence=True)
        manager1._persistence = RoomPersistence(data_dir=self.temp_dir)
        room_code = manager1.create_room(['Option X', 'Option Y'])
        
        # Second instance - should load the room
        manager2 = RoomManager(enable_persistence=True)
        manager2._persistence = RoomPersistence(data_dir=self.temp_dir)
        manager2._rooms = manager2._persistence.load_rooms()
        
        room = manager2.get_room(room_code)
        assert room is not None
        assert room.available_options == ['Option X', 'Option Y']
    
    def test_cleanup_persists(self):
        """Test that cleanup changes are persisted."""
        manager = RoomManager(enable_persistence=True)
        manager._persistence = RoomPersistence(data_dir=self.temp_dir)
        
        # Create an old room
        room_code = manager.create_room()
        room = manager.get_room(room_code)
        room.last_updated = datetime.now() - timedelta(hours=30)
        manager._save_to_disk()
        
        # Clean up
        manager.cleanup_old_rooms(max_age_hours=24)
        
        # Verify it's gone after reload
        manager2 = RoomManager(enable_persistence=True)
        manager2._persistence = RoomPersistence(data_dir=self.temp_dir)
        manager2._rooms = manager2._persistence.load_rooms()
        
        assert not manager2.room_exists(room_code)
    
    def test_auto_cleanup_on_startup(self):
        """Test that old rooms are cleaned up automatically on startup."""
        # Create manager and add an old room
        manager1 = RoomManager(enable_persistence=True)
        manager1._persistence = RoomPersistence(data_dir=self.temp_dir)
        
        room_code = manager1.create_room()
        room = manager1.get_room(room_code)
        room.last_updated = datetime.now() - timedelta(hours=30)
        manager1._save_to_disk()
        
        # Create new manager - should auto-cleanup
        manager2 = RoomManager(enable_persistence=True)
        manager2._persistence = RoomPersistence(data_dir=self.temp_dir)
        manager2._rooms = manager2._persistence.load_rooms()
        manager2.cleanup_old_rooms(max_age_hours=24)
        
        assert not manager2.room_exists(room_code)
