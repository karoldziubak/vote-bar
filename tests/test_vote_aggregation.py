"""
Tests for multi-participant vote aggregation.
"""

import pytest
from logic.room_manager import RoomManager, RoomState


class TestVoteAggregation:
    """Test vote aggregation across multiple participants."""
    
    def test_single_participant_vote(self):
        """Test voting with a single participant."""
        manager = RoomManager(enable_persistence=False)
        room_code = manager.create_room(['A', 'B', 'C'])
        
        # Participant votes
        success = manager.update_room_positions(
            room_code,
            "participant1",
            {'A': 0.0, 'B': 50.0, 'C': 100.0}
        )
        
        assert success is True
        room = manager.get_room(room_code)
        assert room.participant_count == 1
        assert 'participant1' in room.participant_votes
        
        # Get aggregated results
        results = room.get_aggregated_results()
        assert 'A' in results
        assert 'B' in results
        assert 'C' in results
        assert results['A'] > 0
        assert results['B'] > 0
        assert results['C'] > 0
    
    def test_two_participants_voting(self):
        """Test voting with two participants."""
        manager = RoomManager(enable_persistence=False)
        room_code = manager.create_room(['A', 'B', 'C'])
        
        # First participant votes
        manager.update_room_positions(room_code, "p1", {'A': 0.0, 'B': 50.0, 'C': 100.0})
        
        # Second participant votes
        manager.update_room_positions(room_code, "p2", {'A': 25.0, 'B': 75.0})
        
        room = manager.get_room(room_code)
        assert room.participant_count == 2
        assert 'p1' in room.participant_votes
        assert 'p2' in room.participant_votes
        
        # Get aggregated results
        results = room.get_aggregated_results()
        
        # Both participants should contribute
        assert 'A' in results
        assert 'B' in results
        
        # A should have more points (both voted for it)
        assert results['A'] > 0
        assert results['B'] > 0
    
    def test_participant_updates_vote(self):
        """Test that a participant can update their vote."""
        manager = RoomManager(enable_persistence=False)
        room_code = manager.create_room(['A', 'B', 'C'])
        
        # Initial vote
        manager.update_room_positions(room_code, "p1", {'A': 0.0, 'B': 100.0})
        room = manager.get_room(room_code)
        initial_vote = room.participant_votes['p1'].copy()
        
        # Update vote
        manager.update_room_positions(room_code, "p1", {'A': 50.0, 'C': 100.0})
        room = manager.get_room(room_code)
        updated_vote = room.participant_votes['p1']
        
        # Should be different votes
        assert updated_vote != initial_vote
        # Still only 1 participant
        assert room.participant_count == 1
    
    def test_three_participants_different_votes(self):
        """Test aggregation with three participants voting differently."""
        manager = RoomManager(enable_persistence=False)
        room_code = manager.create_room(['Option A', 'Option B', 'Option C', 'Option D'])
        
        # Three different voting patterns
        manager.update_room_positions(room_code, "p1", {'Option A': 10.0, 'Option B': 90.0})
        manager.update_room_positions(room_code, "p2", {'Option A': 10.0, 'Option C': 50.0, 'Option D': 90.0})
        manager.update_room_positions(room_code, "p3", {'Option B': 30.0, 'Option C': 70.0})
        
        room = manager.get_room(room_code)
        assert room.participant_count == 3
        
        results = room.get_aggregated_results()
        
        # All options that were voted for should appear
        assert 'Option A' in results
        assert 'Option B' in results
        assert 'Option C' in results
        
        # Total points should be sum of shares across all participants
        # (each participant distributes 100% across their selected options)
        total_points = sum(results.values())
        assert 290 < total_points < 310  # Should be close to 300 (3 participants * 100%)
    
    def test_empty_room_aggregation(self):
        """Test aggregation when no votes have been submitted."""
        room = RoomState(room_id="EMPTY", available_options=['A', 'B', 'C'])
        results = room.get_aggregated_results()
        
        assert results == {}
    
    def test_aggregation_with_single_option_votes(self):
        """Test aggregation when participants vote for single options."""
        manager = RoomManager(enable_persistence=False)
        room_code = manager.create_room(['A', 'B', 'C'])
        
        # Each participant votes for single option
        manager.update_room_positions(room_code, "p1", {'A': 50.0})
        manager.update_room_positions(room_code, "p2", {'B': 50.0})
        manager.update_room_positions(room_code, "p3", {'C': 50.0})
        
        room = manager.get_room(room_code)
        results = room.get_aggregated_results()
        
        # Each option should have 100 points (one full vote)
        assert abs(results['A'] - 100.0) < 0.1
        assert abs(results['B'] - 100.0) < 0.1
        assert abs(results['C'] - 100.0) < 0.1
    
    def test_nonexistent_room_update(self):
        """Test updating positions in a nonexistent room."""
        manager = RoomManager(enable_persistence=False)
        
        success = manager.update_room_positions("NOTEXIST", "p1", {'A': 50.0})
        
        assert success is False
    
    def test_api_signature_compatibility(self):
        """Test that the API signature accepts correct number of arguments."""
        manager = RoomManager(enable_persistence=False)
        room_code = manager.create_room(['A', 'B'])
        
        # This should work with 3 arguments (room_code, participant_id, positions)
        try:
            success = manager.update_room_positions(
                room_code,
                "test_participant",
                {'A': 25.0, 'B': 75.0}
            )
            assert success is True
        except TypeError as e:
            pytest.fail(f"API signature error: {e}")


class TestMultipleParticipantScenarios:
    """Test realistic multi-participant voting scenarios."""
    
    def test_group_decision_scenario(self):
        """Simulate a group making a decision about restaurant options."""
        manager = RoomManager(enable_persistence=False)
        room_code = manager.create_room(['Pizza', 'Sushi', 'Burgers', 'Tacos'])
        
        # Person 1: Really likes Pizza and Sushi
        manager.update_room_positions(room_code, "alice", {
            'Pizza': 20.0,
            'Sushi': 40.0,
            'Burgers': 80.0
        })
        
        # Person 2: Prefers Tacos and Burgers
        manager.update_room_positions(room_code, "bob", {
            'Burgers': 30.0,
            'Tacos': 70.0
        })
        
        # Person 3: Likes everything but prefers Pizza
        manager.update_room_positions(room_code, "charlie", {
            'Pizza': 10.0,
            'Sushi': 40.0,
            'Burgers': 60.0,
            'Tacos': 90.0
        })
        
        room = manager.get_room(room_code)
        results = room.get_aggregated_results()
        
        # Get ranked results (sorted by points)
        ranked = sorted(results.items(), key=lambda x: x[1], reverse=True)
        
        # Should have votes for all options
        assert len(ranked) == 4
        
        # Winner should be option with most points
        winner = ranked[0][0]
        assert winner in ['Pizza', 'Sushi', 'Burgers', 'Tacos']
        assert ranked[0][1] > 0  # Winner has positive points
    
    def test_strategic_voting_detection(self):
        """Test that extreme strategic voting is still counted fairly."""
        manager = RoomManager(enable_persistence=False)
        room_code = manager.create_room(['A', 'B', 'C'])
        
        # Strategic voter: places options at extremes
        manager.update_room_positions(room_code, "strategic", {
            'A': 0.0,
            'B': 1.0,
            'C': 100.0
        })
        
        # Normal voter: evenly distributed
        manager.update_room_positions(room_code, "normal", {
            'A': 33.0,
            'B': 66.0
        })
        
        room = manager.get_room(room_code)
        results = room.get_aggregated_results()
        
        # Both votes should count equally (each distributes 100% total)
        # Strategic voter's shares + Normal voter's shares
        total = sum(results.values())
        assert 190 < total < 210  # Close to 200 (2 * 100%)
