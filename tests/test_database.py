"""
Unit tests for the Database layer.
"""

import pytest
import tempfile
import gc
import time
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from logic.database import Database, get_database, Room, Vote


@pytest.fixture
def temp_db():
    """Fixture providing a temporary database."""
    tmpdir = tempfile.mkdtemp()
    db_path = str(Path(tmpdir) / "test.db")
    db = Database(db_path)
    
    yield db
    
    # Cleanup
    try:
        db.close()
        gc.collect()
        time.sleep(0.1)
    except Exception:
        pass
    
    try:
        shutil.rmtree(tmpdir, ignore_errors=True)
    except Exception:
        pass


class TestDatabase:
    """Test cases for the Database class."""
    
    def test_database_initialization(self, temp_db):
        """Test database initializes correctly with tables."""
        assert temp_db.db_path.exists()
        assert temp_db.engine is not None
        assert temp_db.SessionLocal is not None
    
    def test_get_session(self, temp_db):
        """Test getting a database session."""
        session = temp_db.get_session()
        assert session is not None
        session.close()
    
    def test_close_connection(self, temp_db):
        """Test closing database connections."""
        temp_db.close()
        # Verify we can still create new connection after close
        session = temp_db.get_session()
        assert session is not None
        session.close()
    
    def test_create_room(self, temp_db):
        """Test creating a room."""
        success = temp_db.create_room("TEST01", ["Option A", "Option B"])
        assert success is True
        
        # Verify room exists
        room = temp_db.get_room("TEST01")
        assert room is not None
        assert room['room_code'] == "TEST01"
        assert room['available_options'] == ["Option A", "Option B"]
    
    def test_create_duplicate_room(self, temp_db):
        """Test creating a room with duplicate code fails."""
        temp_db.create_room("TEST01", ["Option A"])
        success = temp_db.create_room("TEST01", ["Option B"])
        assert success is False
    
    def test_get_nonexistent_room(self, temp_db):
        """Test getting a room that doesn't exist."""
        room = temp_db.get_room("NOEXIST")
        assert room is None
    
    def test_update_room_options(self, temp_db):
        """Test updating room options."""
        temp_db.create_room("TEST01", ["Option A"])
        success = temp_db.update_room_options("TEST01", ["Option A", "Option B", "Option C"])
        assert success is True
        
        room = temp_db.get_room("TEST01")
        assert len(room['available_options']) == 3
    
    def test_update_nonexistent_room_options(self, temp_db):
        """Test updating options for nonexistent room."""
        success = temp_db.update_room_options("NOEXIST", ["Option A"])
        assert success is False
    
    def test_submit_vote(self, temp_db):
        """Test submitting a vote."""
        temp_db.create_room("TEST01", ["Option A", "Option B"])
        positions = {"Option A": 0.3, "Option B": 0.7}
        success = temp_db.submit_vote("TEST01", "participant-1", positions)
        assert success is True
        
        # Verify vote exists
        room = temp_db.get_room("TEST01")
        assert "participant-1" in room['participant_votes']
        assert room['participant_votes']["participant-1"] == positions
    
    def test_submit_vote_nonexistent_room(self, temp_db):
        """Test submitting vote to nonexistent room fails."""
        positions = {"Option A": 0.5}
        success = temp_db.submit_vote("NOEXIST", "participant-1", positions)
        assert success is False
    
    def test_update_existing_vote(self, temp_db):
        """Test updating an existing vote."""
        temp_db.create_room("TEST01", ["Option A", "Option B"])
        temp_db.submit_vote("TEST01", "participant-1", {"Option A": 0.3, "Option B": 0.7})
        
        # Update vote
        new_positions = {"Option A": 0.8, "Option B": 0.2}
        success = temp_db.submit_vote("TEST01", "participant-1", new_positions)
        assert success is True
        
        room = temp_db.get_room("TEST01")
        assert room['participant_votes']["participant-1"] == new_positions
    
    def test_get_all_rooms(self, temp_db):
        """Test getting all rooms."""
        temp_db.create_room("TEST01", ["Option A"])
        temp_db.create_room("TEST02", ["Option B"])
        temp_db.create_room("TEST03", ["Option C"])
        
        rooms = temp_db.get_all_rooms()
        assert len(rooms) >= 3
        room_codes = [r['room_code'] for r in rooms]
        assert "TEST01" in room_codes
        assert "TEST02" in room_codes
        assert "TEST03" in room_codes
    
    def test_cleanup_old_rooms(self, temp_db):
        """Test cleanup of old rooms."""
        # Create a room
        temp_db.create_room("OLD01", ["Option A"])
        temp_db.submit_vote("OLD01", "participant-1", {"Option A": 0.5})
        
        # Manually update timestamp to make it old
        session = temp_db.get_session()
        try:
            old_time = datetime.now() - timedelta(hours=25)
            room = session.query(Room).filter(Room.room_code == "OLD01").first()
            if room:
                room.last_updated = old_time
                session.commit()
        finally:
            session.close()
        
        # Create a new room that shouldn't be deleted
        temp_db.create_room("NEW01", ["Option B"])
        
        # Run cleanup
        deleted_count = temp_db.cleanup_old_rooms(hours=24)
        assert deleted_count == 1
        
        # Verify old room is gone
        assert temp_db.get_room("OLD01") is None
        # Verify new room still exists
        assert temp_db.get_room("NEW01") is not None
    
    def test_cleanup_no_old_rooms(self, temp_db):
        """Test cleanup when no rooms are old."""
        temp_db.create_room("NEW01", ["Option A"])
        temp_db.create_room("NEW02", ["Option B"])
        
        deleted_count = temp_db.cleanup_old_rooms(hours=24)
        assert deleted_count == 0
    
    def test_delete_participant_vote(self, temp_db):
        """Test deleting a participant's vote."""
        temp_db.create_room("TEST01", ["Option A", "Option B"])
        temp_db.submit_vote("TEST01", "participant-1", {"Option A": 0.5, "Option B": 0.5})
        temp_db.submit_vote("TEST01", "participant-2", {"Option A": 0.3, "Option B": 0.7})
        
        # Delete participant-1's vote
        success = temp_db.delete_participant_vote("TEST01", "participant-1")
        assert success is True
        
        # Verify vote is deleted
        room = temp_db.get_room("TEST01")
        assert "participant-1" not in room['participant_votes']
        assert "participant-2" in room['participant_votes']
    
    def test_delete_nonexistent_vote(self, temp_db):
        """Test deleting a vote that doesn't exist."""
        temp_db.create_room("TEST01", ["Option A"])
        success = temp_db.delete_participant_vote("TEST01", "nonexistent")
        assert success is False
    
    def test_room_with_multiple_votes(self, temp_db):
        """Test room correctly aggregates multiple participant votes."""
        temp_db.create_room("TEST01", ["Option A", "Option B", "Option C"])
        temp_db.submit_vote("TEST01", "p1", {"Option A": 0.2, "Option B": 0.5, "Option C": 0.3})
        temp_db.submit_vote("TEST01", "p2", {"Option A": 0.8, "Option B": 0.1, "Option C": 0.1})
        temp_db.submit_vote("TEST01", "p3", {"Option A": 0.5, "Option B": 0.3, "Option C": 0.2})
        
        room = temp_db.get_room("TEST01")
        assert len(room['participant_votes']) == 3
        assert "p1" in room['participant_votes']
        assert "p2" in room['participant_votes']
        assert "p3" in room['participant_votes']


class TestGetDatabaseSingleton:
    """Test cases for the get_database singleton function."""
    
    def test_get_database_returns_singleton(self):
        """Test get_database returns same instance."""
        tmpdir = tempfile.mkdtemp()
        db_path = str(Path(tmpdir) / "singleton.db")
        
        try:
            db1 = get_database(db_path)
            db2 = get_database(db_path)
            assert db1 is db2
        finally:
            try:
                db1.close()
                shutil.rmtree(tmpdir, ignore_errors=True)
            except Exception:
                pass
    
    def test_get_database_force_new(self):
        """Test get_database with force_new creates new instance."""
        tmpdir = tempfile.mkdtemp()
        db_path = str(Path(tmpdir) / "force_new.db")
        
        try:
            db1 = get_database(db_path)
            db2 = get_database(db_path, force_new=True)
            assert db1 is not db2
        finally:
            try:
                db1.close()
                db2.close()
                shutil.rmtree(tmpdir, ignore_errors=True)
            except Exception:
                pass
    
    def test_get_database_different_paths(self):
        """Test get_database with different paths creates different instances."""
        tmpdir = tempfile.mkdtemp()
        db_path1 = str(Path(tmpdir) / "db1.db")
        db_path2 = str(Path(tmpdir) / "db2.db")
        
        try:
            db1 = get_database(db_path1)
            db2 = get_database(db_path2)
            assert db1 is not db2
            assert db1.db_path != db2.db_path
        finally:
            try:
                db1.close()
                db2.close()
                shutil.rmtree(tmpdir, ignore_errors=True)
            except Exception:
                pass


class TestDatabaseErrorHandling:
    """Test error handling in database operations."""
    
    def test_update_room_options_handles_errors(self, temp_db):
        """Test update_room_options handles database errors gracefully."""
        # Try to update room that doesn't exist - should return False
        result = temp_db.update_room_options("NONEXISTENT", ["Option A"])
        assert result is False
    
    def test_submit_vote_validates_room_exists(self, temp_db):
        """Test submit_vote validates room exists before inserting vote."""
        # Try to vote in nonexistent room
        result = temp_db.submit_vote("NONEXISTENT", "participant-1", {"Option A": 0.5})
        assert result is False
    
    def test_cleanup_with_no_rooms(self, temp_db):
        """Test cleanup_old_rooms works with empty database."""
        deleted = temp_db.cleanup_old_rooms(hours=24)
        assert deleted == 0
    
    def test_delete_room(self, temp_db):
        """Test deleting a room and its votes."""
        temp_db.create_room("TEST01", ["Option A", "Option B"])
        temp_db.submit_vote("TEST01", "p1", {"Option A": 0.5, "Option B": 0.5})
        temp_db.submit_vote("TEST01", "p2", {"Option A": 0.3, "Option B": 0.7})
        
        # Delete room
        success = temp_db.delete_room("TEST01")
        assert success is True
        
        # Verify room and votes are gone
        assert temp_db.get_room("TEST01") is None
    
    def test_delete_nonexistent_room(self, temp_db):
        """Test deleting a room that doesn't exist."""
        success = temp_db.delete_room("NONEXISTENT")
        assert success is False
    
    def test_room_exists(self, temp_db):
        """Test room_exists method."""
        temp_db.create_room("TEST01", ["Option A"])
        assert temp_db.room_exists("TEST01") is True
        assert temp_db.room_exists("NONEXISTENT") is False
    
    def test_get_participant_vote(self, temp_db):
        """Test getting a specific participant's vote."""
        temp_db.create_room("TEST01", ["Option A", "Option B"])
        positions = {"Option A": 0.6, "Option B": 0.4}
        temp_db.submit_vote("TEST01", "p1", positions)
        
        vote = temp_db.get_participant_vote("TEST01", "p1")
        assert vote == positions
        
        # Test nonexistent participant
        vote = temp_db.get_participant_vote("TEST01", "nonexistent")
        assert vote is None
    
    def test_get_all_votes(self, temp_db):
        """Test getting all votes for a room."""
        temp_db.create_room("TEST01", ["Option A", "Option B"])
        temp_db.submit_vote("TEST01", "p1", {"Option A": 0.6, "Option B": 0.4})
        temp_db.submit_vote("TEST01", "p2", {"Option A": 0.3, "Option B": 0.7})
        
        all_votes = temp_db.get_all_votes("TEST01")
        assert len(all_votes) == 2
        assert "p1" in all_votes
        assert "p2" in all_votes
    
    def test_close_handles_errors_gracefully(self):
        """Test close() handles errors when pool doesn't exist."""
        tmpdir = tempfile.mkdtemp()
        db_path = str(Path(tmpdir) / "test.db")
        db = Database(db_path)
        
        # Dispose engine first to simulate error condition
        db.engine.dispose()
        
        # close() should handle this gracefully
        db.close()  # Should not raise exception
        
        # Cleanup
        try:
            shutil.rmtree(tmpdir, ignore_errors=True)
        except Exception:
            pass
