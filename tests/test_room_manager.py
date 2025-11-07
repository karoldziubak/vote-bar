"""
Unit tests for room management functionality.
"""

from datetime import datetime, timedelta
from logic.room_manager import RoomManager, RoomState, get_room_manager


class TestRoomManager:
    """Test cases for the RoomManager class."""
    
    def test_create_room(self):
        """Test creating a new room."""
        manager = RoomManager(enable_persistence=False)
        
        room_code = manager.create_room()
        
        assert room_code is not None
        assert len(room_code) == 6
        assert room_code.isalnum()
        assert manager.room_exists(room_code)
    
    def test_create_room_with_options(self):
        """Test creating a room with initial options."""
        manager = RoomManager(enable_persistence=False)
        initial_options = ['Red', 'Blue', 'Green']
        
        room_code = manager.create_room(initial_options)
        room = manager.get_room(room_code)
        
        assert room is not None
        assert room.available_options == initial_options
    
    def test_join_existing_room(self):
        """Test joining an existing room."""
        manager = RoomManager(enable_persistence=False)
        
        room_code = manager.create_room()
        room = manager.join_room(room_code)
        
        assert room is not None
        assert room.room_id == room_code
        assert room.participant_count == 2  # Creator + joiner
    
    def test_join_nonexistent_room(self):
        """Test joining a room that doesn't exist."""
        manager = RoomManager(enable_persistence=False)
        
        room = manager.join_room("XXXXXX")
        
        assert room is None
    
    def test_update_room_options(self):
        """Test updating options in a room."""
        manager = RoomManager(enable_persistence=False)
        
        room_code = manager.create_room(['A', 'B'])
        new_options = ['A', 'B', 'C']
        
        success = manager.update_room_options(room_code, new_options)
        room = manager.get_room(room_code)
        
        assert success is True
        assert room.available_options == new_options
    
    def test_update_room_options_nonexistent(self):
        """Test updating options in a nonexistent room."""
        manager = RoomManager(enable_persistence=False)
        
        success = manager.update_room_options("XXXXXX", ['A', 'B'])
        
        assert success is False
    
    def test_update_room_positions(self):
        """Test updating positions in a room."""
        manager = RoomManager(enable_persistence=False)
        
        room_code = manager.create_room()
        positions = {'Option A': 25.0, 'Option B': 75.0}
        participant_id = "test_participant"
        
        success = manager.update_room_positions(room_code, participant_id, positions)
        room = manager.get_room(room_code)
        
        assert success is True
        assert participant_id in room.participant_votes
        assert room.participant_votes[participant_id] == positions
    
    def test_update_room_positions_nonexistent(self):
        """Test updating positions in a nonexistent room."""
        manager = RoomManager(enable_persistence=False)
        
        success = manager.update_room_positions("XXXXXX", "test_participant", {'A': 50.0})
        
        assert success is False
    
    def test_room_code_case_insensitive(self):
        """Test that room codes are case-insensitive."""
        manager = RoomManager(enable_persistence=False)
        
        room_code = manager.create_room()
        room_lower = manager.get_room(room_code.lower())
        room_upper = manager.get_room(room_code.upper())
        
        assert room_lower is not None
        assert room_upper is not None
        assert room_lower.room_id == room_upper.room_id
    
    def test_unique_room_codes(self):
        """Test that generated room codes are unique."""
        manager = RoomManager(enable_persistence=False)
        
        codes = set()
        for _ in range(100):
            code = manager.create_room()
            assert code not in codes
            codes.add(code)
    
    def test_get_room_count(self):
        """Test getting the total number of rooms."""
        manager = RoomManager(enable_persistence=False)
        
        assert manager.get_room_count() == 0
        
        manager.create_room()
        assert manager.get_room_count() == 1
        
        manager.create_room()
        manager.create_room()
        assert manager.get_room_count() == 3
    
    def test_cleanup_old_rooms(self):
        """Test cleaning up old inactive rooms."""
        manager = RoomManager(enable_persistence=False)
        
        # Create a room
        room_code = manager.create_room()
        room = manager.get_room(room_code)
        
        # Manually set last_updated to old timestamp
        room.last_updated = datetime.now() - timedelta(hours=25)
        
        # Clean up rooms older than 24 hours
        cleaned = manager.cleanup_old_rooms(max_age_hours=24)
        
        assert cleaned == 1
        assert not manager.room_exists(room_code)
    
    def test_cleanup_no_old_rooms(self):
        """Test cleanup when no rooms are old enough."""
        manager = RoomManager(enable_persistence=False)
        
        # Create fresh rooms
        manager.create_room()
        manager.create_room()
        
        # Try to clean up rooms older than 24 hours
        cleaned = manager.cleanup_old_rooms(max_age_hours=24)
        
        assert cleaned == 0
        assert manager.get_room_count() == 2
    
    def test_cleanup_mixed_rooms(self):
        """Test cleanup with mix of old and new rooms."""
        manager = RoomManager(enable_persistence=False)
        
        # Create an old room
        old_code = manager.create_room()
        old_room = manager.get_room(old_code)
        old_room.last_updated = datetime.now() - timedelta(hours=30)
        
        # Create a fresh room
        new_code = manager.create_room()
        
        # Clean up
        cleaned = manager.cleanup_old_rooms(max_age_hours=24)
        
        assert cleaned == 1
        assert not manager.room_exists(old_code)
        assert manager.room_exists(new_code)


class TestRoomState:
    """Test cases for the RoomState class."""
    
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


class TestGetRoomManager:
    """Test cases for the get_room_manager singleton."""
    
    def test_get_room_manager_singleton(self):
        """Test that get_room_manager returns the same instance."""
        manager1 = get_room_manager()
        manager2 = get_room_manager()
        
        assert manager1 is manager2
    
    def test_get_room_manager_creates_instance(self):
        """Test that get_room_manager creates an instance."""
        manager = get_room_manager()
        
        assert manager is not None
        assert isinstance(manager, RoomManager)
    
    def test_singleton_state_persistence(self):
        """Test that room state persists across get_room_manager calls."""
        manager1 = get_room_manager()
        room_code = manager1.create_room()
        
        manager2 = get_room_manager()
        room = manager2.get_room(room_code)
        
        assert room is not None
        assert room.room_id == room_code
