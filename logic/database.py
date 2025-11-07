"""
SQLite database models and initialization for vote-bar persistence.

Uses SQLAlchemy ORM for database operations.
Tables:
- rooms: Store room metadata (code, options, creation time, last update)
- votes: Store individual participant votes (room_code, participant_id, positions)
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from sqlalchemy import create_engine, Column, String, DateTime, JSON, PrimaryKeyConstraint
from sqlalchemy.orm import declarative_base, sessionmaker, Session

Base = declarative_base()


class Room(Base):
    """Room table storing room metadata and available options."""
    __tablename__ = 'rooms'
    
    room_code = Column(String(6), primary_key=True, index=True)
    available_options = Column(JSON, nullable=False)  # List of option strings
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    last_updated = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    
    def __repr__(self):
        return f"<Room(code={self.room_code}, options={len(self.available_options)}, updated={self.last_updated})>"


class Vote(Base):
    """Vote table storing individual participant votes in rooms."""
    __tablename__ = 'votes'
    
    room_code = Column(String(6), nullable=False)
    participant_id = Column(String(36), nullable=False)  # UUID
    positions = Column(JSON, nullable=False)  # Dict[str, float] - option -> position
    submitted_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    
    # Composite primary key: one vote per participant per room
    __table_args__ = (
        PrimaryKeyConstraint('room_code', 'participant_id'),
    )
    
    def __repr__(self):
        return f"<Vote(room={self.room_code}, participant={self.participant_id[:8]}..., options={len(self.positions)})>"


class Database:
    """Database manager for vote-bar SQLite operations."""
    
    def __init__(self, db_path: str = "data/vote_bar.db"):
        """Initialize database connection and create tables if needed."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create engine with connection pooling
        self.engine = create_engine(
            f"sqlite:///{self.db_path}",
            echo=False,  # Set to True for SQL debugging
            connect_args={"check_same_thread": False}  # Allow multi-threaded access
        )
        
        # Create tables if they don't exist
        Base.metadata.create_all(self.engine)
        
        # Session factory
        self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)
    
    def get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()
    
    def close(self) -> None:
        """Close database connections and dispose engine."""
        try:
            # Force close any remaining connections
            self.engine.pool.dispose()
        except Exception:
            pass
        # Dispose the engine (closes connection pool)
        self.engine.dispose()
    
    def cleanup_old_rooms(self, hours: int = 24) -> int:
        """Delete rooms that haven't been updated in the specified hours."""
        cutoff = datetime.now() - timedelta(hours=hours)
        session = self.get_session()
        try:
            # Delete old votes first (foreign key constraint)
            old_rooms = session.query(Room).filter(Room.last_updated < cutoff).all()
            old_room_codes = [room.room_code for room in old_rooms]
            
            if old_room_codes:
                session.query(Vote).filter(Vote.room_code.in_(old_room_codes)).delete(synchronize_session=False)
                deleted_count = session.query(Room).filter(Room.room_code.in_(old_room_codes)).delete(synchronize_session=False)
                session.commit()
                return deleted_count
            return 0
        finally:
            session.close()
    
    # Room operations
    def create_room(self, room_code: str, available_options: List[str]) -> bool:
        """Create a new room."""
        session = self.get_session()
        try:
            room = Room(
                room_code=room_code,
                available_options=available_options,
                created_at=datetime.now(),
                last_updated=datetime.now()
            )
            session.add(room)
            session.commit()
            return True
        except Exception:
            session.rollback()
            return False
        finally:
            session.close()
    
    def get_room(self, room_code: str) -> Optional[Dict]:
        """Get room data by code."""
        session = self.get_session()
        try:
            room = session.query(Room).filter(Room.room_code == room_code).first()
            if not room:
                return None
            
            # Get all votes for this room
            votes = session.query(Vote).filter(Vote.room_code == room_code).all()
            participant_votes = {
                vote.participant_id: vote.positions 
                for vote in votes
            }
            
            return {
                'room_code': room.room_code,
                'available_options': room.available_options,
                'created_at': room.created_at,
                'last_updated': room.last_updated,
                'participant_votes': participant_votes
            }
        finally:
            session.close()
    
    def room_exists(self, room_code: str) -> bool:
        """Check if a room exists."""
        session = self.get_session()
        try:
            return session.query(Room).filter(Room.room_code == room_code).count() > 0
        finally:
            session.close()
    
    def update_room_options(self, room_code: str, available_options: List[str]) -> bool:
        """Update room's available options."""
        session = self.get_session()
        try:
            room = session.query(Room).filter(Room.room_code == room_code).first()
            if not room:
                return False
            
            room.available_options = available_options
            room.last_updated = datetime.now()
            session.commit()
            return True
        except Exception:
            session.rollback()
            return False
        finally:
            session.close()
    
    def delete_room(self, room_code: str) -> bool:
        """Delete a room and all its votes."""
        session = self.get_session()
        try:
            # Delete votes first
            session.query(Vote).filter(Vote.room_code == room_code).delete()
            # Delete room
            deleted = session.query(Room).filter(Room.room_code == room_code).delete()
            session.commit()
            return deleted > 0
        except Exception:
            session.rollback()
            return False
        finally:
            session.close()
    
    def get_all_rooms(self) -> List[Dict]:
        """Get all rooms (for testing/debugging)."""
        session = self.get_session()
        try:
            rooms = session.query(Room).all()
            result = []
            for room in rooms:
                votes = session.query(Vote).filter(Vote.room_code == room.room_code).all()
                participant_votes = {
                    vote.participant_id: vote.positions 
                    for vote in votes
                }
                result.append({
                    'room_code': room.room_code,
                    'available_options': room.available_options,
                    'created_at': room.created_at,
                    'last_updated': room.last_updated,
                    'participant_votes': participant_votes
                })
            return result
        finally:
            session.close()
    
    # Vote operations
    def submit_vote(self, room_code: str, participant_id: str, positions: Dict[str, float]) -> bool:
        """Submit or update a participant's vote in a room."""
        session = self.get_session()
        try:
            # First check if room exists
            room = session.query(Room).filter(Room.room_code == room_code).first()
            if not room:
                return False
            
            # Check if vote already exists
            existing_vote = session.query(Vote).filter(
                Vote.room_code == room_code,
                Vote.participant_id == participant_id
            ).first()
            
            if existing_vote:
                # Update existing vote
                existing_vote.positions = positions
                existing_vote.submitted_at = datetime.now()
            else:
                # Create new vote
                vote = Vote(
                    room_code=room_code,
                    participant_id=participant_id,
                    positions=positions,
                    submitted_at=datetime.now()
                )
                session.add(vote)
            
            # Update room's last_updated timestamp
            room.last_updated = datetime.now()
            
            session.commit()
            return True
        except Exception:
            session.rollback()
            return False
        finally:
            session.close()
    
    def get_participant_vote(self, room_code: str, participant_id: str) -> Optional[Dict[str, float]]:
        """Get a specific participant's vote in a room."""
        session = self.get_session()
        try:
            vote = session.query(Vote).filter(
                Vote.room_code == room_code,
                Vote.participant_id == participant_id
            ).first()
            return vote.positions if vote else None
        finally:
            session.close()
    
    def get_all_votes(self, room_code: str) -> Dict[str, Dict[str, float]]:
        """Get all votes for a room."""
        session = self.get_session()
        try:
            votes = session.query(Vote).filter(Vote.room_code == room_code).all()
            return {vote.participant_id: vote.positions for vote in votes}
        finally:
            session.close()
    
    def delete_participant_vote(self, room_code: str, participant_id: str) -> bool:
        """Delete a participant's vote from a room."""
        session = self.get_session()
        try:
            deleted = session.query(Vote).filter(
                Vote.room_code == room_code,
                Vote.participant_id == participant_id
            ).delete()
            session.commit()
            return deleted > 0
        except Exception:
            session.rollback()
            return False
        finally:
            session.close()


# Global database instance (for production use)
_db_instance: Optional[Database] = None


def get_database(db_path: str = "data/vote_bar.db", force_new: bool = False) -> Database:
    """
    Get or create the global database instance.
    
    Args:
        db_path: Path to the database file
        force_new: If True, create a new instance even if one exists
    """
    global _db_instance
    if force_new or _db_instance is None or _db_instance.db_path != Path(db_path):
        _db_instance = Database(db_path)
    return _db_instance
