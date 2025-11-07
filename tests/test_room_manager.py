"""
Unit tests for room management functionality with SQLite backend.
"""

import pytest
import tempfile
import gc
import time
from pathlib import Path
from datetime import datetime, timedelta
from logic.room_manager import RoomManager, RoomState


@pytest.fixture
def temp_manager():
    """Fixture providing a RoomManager with temporary database."""
    tmpdir = tempfile.mkdtemp()
    db_path = str(Path(tmpdir) / "test.db")
    manager = RoomManager(db_path=db_path)
    
    yield manager
    
    # Clean up: close all database connections
    try:
        manager.db.close()
        # Force garbage collection to release file handles
        gc.collect()
        time.sleep(0.15)  # Increased delay for Windows
    except Exception:
        pass  # Ignore cleanup errors
    
    # Force new instance for next test
    try:
        from logic.database import get_database
        get_database(db_path, force_new=True)
    except Exception:
        pass
    
    # Try to clean up temp directory (best effort on Windows)
    try:
        import shutil
        time.sleep(0.1)
        shutil.rmtree(tmpdir, ignore_errors=True)
    except Exception:
        pass  # Windows may still have file locks


class TestRoomManager:
    """Test cases for the RoomManager class with SQLite backend."""
    
    def test_create_room(self, temp_manager):
        """Test creating a new room."""
        room_code = temp_manager.create_room()
        
        assert room_code is not None
        assert len(room_code) == 6
        assert room_code.isalnum()
        assert temp_manager.room_exists(room_code)
    
    def test_create_room_with_options(self, temp_manager):
        """Test creating a room with initial options."""
        initial_options = ['Red', 'Blue', 'Green']
        
        room_code = temp_manager.create_room(initial_options)
        room = temp_manager.get_room(room_code)
        
        assert room is not None
        assert room.available_options == initial_options
    
    def test_join_existing_room(self, temp_manager):
        """Test joining an existing room."""
        room_code = temp_manager.create_room()
        room = temp_manager.join_room(room_code)
        
        assert room is not None
        assert room.room_id == room_code
    
    def test_join_nonexistent_room(self, temp_manager):
        """Test joining a room that doesn't exist."""
        room = temp_manager.join_room("XXXXXX")
        
        assert room is None
    
    def test_update_room_options(self, temp_manager):
        """Test updating options in a room."""
        room_code = temp_manager.create_room(['A', 'B'])
        new_options = ['A', 'B', 'C']
        
        success = temp_manager.update_room_options(room_code, new_options)
        room = temp_manager.get_room(room_code)
        
        assert success is True
        assert room.available_options == new_options
    
    def test_update_room_options_nonexistent(self, temp_manager):
        """Test updating options in a nonexistent room."""
        success = temp_manager.update_room_options("XXXXXX", ['A', 'B'])
        
        assert success is False
    
    def test_update_room_positions(self, temp_manager):
        """Test updating positions in a room."""
        room_code = temp_manager.create_room()
        positions = {'Option A': 25.0, 'Option B': 75.0}
        participant_id = "test_participant"
        
        success = temp_manager.update_room_positions(room_code, participant_id, positions)
        room = temp_manager.get_room(room_code)
        
        assert success is True
        assert participant_id in room.participant_votes
        assert room.participant_votes[participant_id] == positions
    
    def test_update_room_positions_nonexistent(self, temp_manager):
        """Test updating positions in a nonexistent room."""
        success = temp_manager.update_room_positions("XXXXXX", "test_participant", {'A': 50.0})
        
        assert success is False
    
    def test_room_code_case_insensitive(self, temp_manager):
        """Test that room codes are case-insensitive."""
        room_code = temp_manager.create_room()
        room_lower = temp_manager.get_room(room_code.lower())
        room_upper = temp_manager.get_room(room_code.upper())
        
        assert room_lower is not None
        assert room_upper is not None
        assert room_lower.room_id == room_upper.room_id
    
    def test_unique_room_codes(self, temp_manager):
        """Test that generated room codes are unique."""
        codes = set()
        for _ in range(100):
            code = temp_manager.create_room()
            assert code not in codes
            codes.add(code)
    
    def test_get_room_count(self, temp_manager):
        """Test getting the total number of rooms."""
        assert temp_manager.get_room_count() == 0
        
        temp_manager.create_room()
        assert temp_manager.get_room_count() == 1
        
        temp_manager.create_room()
        temp_manager.create_room()
        assert temp_manager.get_room_count() == 3
    
    def test_cleanup_old_rooms(self):
        """Test cleaning up old inactive rooms."""
        import shutil
        tmpdir = tempfile.mkdtemp()
        try:
            db_path = str(Path(tmpdir) / "test.db")
            manager = RoomManager(db_path=db_path)
            
            # Create a room
            room_code = manager.create_room()
            
            # Directly manipulate database to set old timestamp
            from logic.database import get_database, Room
            db = get_database(db_path)
            old_time = datetime.now() - timedelta(hours=25)
            session = db.get_session()
            try:
                room = session.query(Room).filter(Room.room_code == room_code).first()
                room.last_updated = old_time
                session.commit()
            finally:
                session.close()
            
            # Clean up rooms older than 24 hours
            cleaned = manager.cleanup_old_rooms(max_age_hours=24)
            
            assert cleaned == 1
            assert not manager.room_exists(room_code)
            
            # Clean up database connections
            manager.db.close()
            db.close()
            gc.collect()
            time.sleep(0.2)
        finally:
            # Best effort cleanup
            try:
                shutil.rmtree(tmpdir, ignore_errors=True)
            except Exception:
                pass
    
    def test_cleanup_no_old_rooms(self, temp_manager):
        """Test cleanup when no rooms are old enough."""
        # Create fresh rooms
        temp_manager.create_room()
        temp_manager.create_room()
        
        # Try to clean up rooms older than 24 hours
        cleaned = temp_manager.cleanup_old_rooms(max_age_hours=24)
        
        assert cleaned == 0
        assert temp_manager.get_room_count() == 2
    
    def test_submit_vote(self, temp_manager):
        """Test submitting a vote updates room."""
        room_code = temp_manager.create_room()
        participant_id = "test_user"
        positions = {'Option A': 20.0, 'Option B': 80.0}
        
        success = temp_manager.update_room_positions(room_code, participant_id, positions)
        assert success
        
        # Verify vote is stored
        room = temp_manager.get_room(room_code)
        assert participant_id in room.participant_votes
        assert room.participant_votes[participant_id] == positions
    
    def test_get_aggregated_results(self, temp_manager):
        """Test aggregating results from multiple participants."""
        room_code = temp_manager.create_room(['A', 'B', 'C'])
        
        # Participant 1
        temp_manager.update_room_positions(room_code, "p1", {'A': 0.0, 'B': 50.0, 'C': 100.0})
        
        # Participant 2
        temp_manager.update_room_positions(room_code, "p2", {'A': 25.0, 'B': 75.0})
        
        room = temp_manager.get_room(room_code)
        results = room.get_aggregated_results()
        
        # Both participants should contribute
        assert 'A' in results
        assert 'B' in results
        assert results['A'] > 0
        assert results['B'] > 0


class TestRoomState:
    """Test cases for the RoomState dataclass."""
    
    def test_submit_vote(self):
        """Test submitting a vote in room state."""
        state = RoomState(room_id="TEST")
        positions = {'A': 10.0, 'B': 90.0}
        participant_id = "participant_1"
        
        initial_time = state.last_updated
        state.submit_vote(participant_id, positions)
        
        assert participant_id in state.participant_votes
        assert state.participant_votes[participant_id] == positions
        assert state.last_updated > initial_time
        assert state.participant_count == 1
    
    def test_get_aggregated_results(self):
        """Test aggregating votes from multiple participants."""
        state = RoomState(room_id="TEST", available_options=['A', 'B', 'C'])
        
        # Participant 1 votes: A at 0, B at 50, C at 100
        state.submit_vote("p1", {'A': 0.0, 'B': 50.0, 'C': 100.0})
        
        # Participant 2 votes: A at 25, B at 75
        state.submit_vote("p2", {'A': 25.0, 'B': 75.0})
        
        results = state.get_aggregated_results()
        
        # Both participants should contribute
        assert 'A' in results
        assert 'B' in results
        assert results['A'] > 0
        assert results['B'] > 0
        assert state.participant_count == 2
    
    def test_update_options(self):
        """Test updating options in room state."""
        state = RoomState(room_id="TEST")
        options = ['X', 'Y', 'Z']
        
        initial_time = state.last_updated
        state.update_options(options)
        
        assert state.available_options == options
        assert state.last_updated > initial_time
