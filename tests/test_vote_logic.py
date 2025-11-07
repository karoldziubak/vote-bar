"""
Unit tests for the vote-bar logic.
"""

import pandas as pd
from logic.vote_logic import VoteBar, PositionVote


class TestPositionVote:
    """Test cases for the PositionVote class."""
    
    def test_position_vote_init(self):
        """Test PositionVote initialization."""
        positions = {"A": (0.0, 50.0), "B": (50.0, 100.0)}
        vote = PositionVote(positions)
        
        assert vote.option_positions == positions
        assert vote.percentages["A"] == 50.0
        assert vote.percentages["B"] == 50.0
    
    def test_position_vote_calculate_percentages(self):
        """Test percentage calculation from positions."""
        positions = {"A": (10.0, 60.0), "B": (70.0, 90.0)}
        vote = PositionVote(positions)
        
        assert vote.percentages["A"] == 50.0  # 60 - 10
        assert vote.percentages["B"] == 20.0  # 90 - 70


class TestVoteBar:
    """Test cases for the VoteBar class."""
    
    def test_init(self):
        """Test VoteBar initialization."""
        options = ["Option A", "Option B", "Option C"]
        vote_bar = VoteBar(options)
        
        assert vote_bar.options == options
        assert vote_bar.votes == []
    
    def test_add_valid_vote(self):
        """Test adding a valid vote."""
        vote_bar = VoteBar(["A", "B", "C"])
        vote = {"A": 50.0, "B": 30.0, "C": 20.0}
        
        result = vote_bar.add_vote(vote)
        
        assert result is True
        assert len(vote_bar.votes) == 1
        assert isinstance(vote_bar.votes[0], PositionVote)
        # Check that percentages are calculated correctly
        assert vote_bar.votes[0].percentages["A"] == 50.0
        assert vote_bar.votes[0].percentages["B"] == 30.0
        assert vote_bar.votes[0].percentages["C"] == 20.0
    
    def test_add_invalid_vote_wrong_total(self):
        """Test adding a vote that doesn't sum to 100%."""
        vote_bar = VoteBar(["A", "B", "C"])
        vote = {"A": 50.0, "B": 30.0, "C": 15.0}  # Sums to 95%
        
        result = vote_bar.add_vote(vote)
        
        assert result is False
        assert len(vote_bar.votes) == 0
    
    def test_add_invalid_vote_negative_value(self):
        """Test adding a vote with negative percentages."""
        vote_bar = VoteBar(["A", "B", "C"])
        vote = {"A": 110.0, "B": -10.0, "C": 0.0}  # Negative value
        
        result = vote_bar.add_vote(vote)
        
        assert result is False
        assert len(vote_bar.votes) == 0
    
    def test_add_invalid_vote_unknown_option(self):
        """Test adding a vote with unknown options."""
        vote_bar = VoteBar(["A", "B", "C"])
        vote = {"A": 50.0, "D": 50.0}  # "D" is not a valid option
        
        result = vote_bar.add_vote(vote)
        
        assert result is False
        assert len(vote_bar.votes) == 0
    
    def test_get_results_empty(self):
        """Test getting results when no votes have been cast."""
        vote_bar = VoteBar(["A", "B", "C"])
        
        results = vote_bar.get_results()
        
        assert isinstance(results, pd.DataFrame)
        assert len(results) == 0
        assert list(results.columns) == ['option', 'average_score', 'total_votes']
    
    def test_get_results_with_votes(self):
        """Test getting results with multiple votes."""
        vote_bar = VoteBar(["A", "B", "C"])
        
        # Add some test votes
        vote_bar.add_vote({"A": 60.0, "B": 40.0, "C": 0.0})
        vote_bar.add_vote({"A": 40.0, "B": 20.0, "C": 40.0})
        vote_bar.add_vote({"A": 0.0, "B": 50.0, "C": 50.0})
        
        results = vote_bar.get_results()
        
        assert len(results) == 3
        assert results.iloc[0]['option'] == 'B'  # Highest average (36.67%)
        assert abs(results.iloc[0]['average_score'] - 36.67) < 0.01
        
    def test_partial_votes(self):
        """Test that votes can include only some options (others default to 0)."""
        vote_bar = VoteBar(["A", "B", "C"])
        vote = {"A": 100.0}  # Only vote for A
        
        result = vote_bar.add_vote(vote)
        results = vote_bar.get_results()
        
        assert result is True
        assert results.loc[results['option'] == 'A', 'average_score'].iloc[0] == 100.0
        assert results.loc[results['option'] == 'B', 'average_score'].iloc[0] == 0.0
        assert results.loc[results['option'] == 'C', 'average_score'].iloc[0] == 0.0
    
    def test_add_position_vote_valid(self):
        """Test adding a valid position-based vote."""
        vote_bar = VoteBar(["A", "B", "C"])
        positions = {"A": (0.0, 50.0), "B": (60.0, 100.0)}
        
        result = vote_bar.add_position_vote(positions)
        
        assert result is True
        assert len(vote_bar.votes) == 1
        assert isinstance(vote_bar.votes[0], PositionVote)
    
    def test_add_position_vote_overlapping(self):
        """Test adding position vote with overlapping ranges."""
        vote_bar = VoteBar(["A", "B", "C"])
        positions = {"A": (0.0, 50.0), "B": (40.0, 80.0)}  # Overlapping
        
        result = vote_bar.add_position_vote(positions)
        
        assert result is False
        assert len(vote_bar.votes) == 0
    
    def test_add_position_vote_invalid_range(self):
        """Test adding position vote with invalid ranges."""
        vote_bar = VoteBar(["A", "B", "C"])
        positions = {"A": (-10.0, 50.0), "B": (60.0, 110.0)}  # Out of 0-100 range
        
        result = vote_bar.add_position_vote(positions)
        
        assert result is False
        assert len(vote_bar.votes) == 0
    
    def test_add_position_vote_unknown_option(self):
        """Test adding position vote with unknown option."""
        vote_bar = VoteBar(["A", "B", "C"])
        positions = {"A": (0.0, 50.0), "D": (60.0, 80.0)}  # "D" is unknown
        
        result = vote_bar.add_position_vote(positions)
        
        assert result is False
        assert len(vote_bar.votes) == 0
    
    def test_get_results_with_position_votes(self):
        """Test getting results with position-based votes."""
        vote_bar = VoteBar(["A", "B", "C"])
        
        # Add position votes
        vote_bar.add_position_vote({"A": (0.0, 60.0), "B": (60.0, 100.0)})  # A=60%, B=40%
        vote_bar.add_position_vote({"A": (0.0, 30.0), "C": (30.0, 100.0)})  # A=30%, C=70%
        
        results = vote_bar.get_results()
        
        assert len(results) == 3
        # A: average = (60 + 30) / 2 = 45%
        assert abs(results.loc[results['option'] == 'A', 'average_score'].iloc[0] - 45.0) < 0.01
        # B: average = (40 + 0) / 2 = 20%
        assert abs(results.loc[results['option'] == 'B', 'average_score'].iloc[0] - 20.0) < 0.01
        # C: average = (0 + 70) / 2 = 35%
        assert abs(results.loc[results['option'] == 'C', 'average_score'].iloc[0] - 35.0) < 0.01
    
    def test_get_position_summary(self):
        """Test getting position summary."""
        vote_bar = VoteBar(["A", "B", "C"])
        
        vote_bar.add_position_vote({"A": (0.0, 50.0), "B": (50.0, 100.0)})
        vote_bar.add_position_vote({"A": (10.0, 40.0), "C": (60.0, 90.0)})
        
        summary = vote_bar.get_position_summary()
        
        assert len(summary["A"]) == 2
        assert summary["A"] == [(0.0, 50.0), (10.0, 40.0)]
        assert len(summary["B"]) == 1
        assert summary["B"] == [(50.0, 100.0)]
        assert len(summary["C"]) == 1
        assert summary["C"] == [(60.0, 90.0)]
    
    def test_mixed_vote_types(self):
        """Test handling both traditional and position-based votes."""
        vote_bar = VoteBar(["A", "B", "C"])
        
        # Add traditional vote
        vote_bar.add_vote({"A": 50.0, "B": 50.0})
        
        # Add position vote
        vote_bar.add_position_vote({"A": (0.0, 30.0), "C": (30.0, 100.0)})
        
        results = vote_bar.get_results()
        
        assert len(results) == 3
        # Should handle both vote types correctly
        assert len(vote_bar.votes) == 2