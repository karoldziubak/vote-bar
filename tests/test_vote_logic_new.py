"""
Unit tests for the simplified vote-bar logic.
"""

import pytest
from logic.vote_logic import compute_vote_shares, VoteResult


class TestComputeVoteShares:
    """Test cases for the compute_vote_shares function."""
    
    def test_empty_positions(self):
        """Test with no positions."""
        result = compute_vote_shares({})
        assert result == {}
    
    def test_single_option(self):
        """Test with single option gets 100%."""
        result = compute_vote_shares({"A": 50.0})
        assert result == {"A": 100.0}
        
        # Position doesn't matter for single option
        result = compute_vote_shares({"A": 25.0})
        assert result == {"A": 100.0}
    
    def test_two_options_equal_split(self):
        """Test two options with equal split."""
        result = compute_vote_shares({"A": 30.0, "B": 70.0})
        assert result == {"A": 50.0, "B": 50.0}
    
    def test_two_options_unequal_positions(self):
        """Test two options with different spacing."""
        result = compute_vote_shares({"A": 10.0, "B": 90.0})
        assert result == {"A": 50.0, "B": 50.0}  # Always 50/50 for two options
    
    def test_three_options_even_spacing(self):
        """Test three options with even spacing."""
        result = compute_vote_shares({"A": 20.0, "B": 50.0, "C": 80.0})
        expected = {"A": 35.0, "B": 30.0, "C": 35.0}
        assert result == expected
    
    def test_three_options_uneven_spacing(self):
        """Test three options with uneven spacing."""
        result = compute_vote_shares({"A": 10.0, "B": 20.0, "C": 90.0})
        # Midpoints: 15 (between A and B), 55 (between B and C)
        # A: 0-15 = 15%, B: 15-55 = 40%, C: 55-100 = 45%
        expected = {"A": 15.0, "B": 40.0, "C": 45.0}
        assert result == expected
    
    def test_options_order_independence(self):
        """Test that order of input doesn't matter."""
        positions1 = {"A": 20.0, "B": 50.0, "C": 80.0}
        positions2 = {"C": 80.0, "A": 20.0, "B": 50.0}
        
        result1 = compute_vote_shares(positions1)
        result2 = compute_vote_shares(positions2)
        
        assert result1 == result2
    
    def test_extreme_positions(self):
        """Test with positions at boundaries."""
        result = compute_vote_shares({"A": 0.0, "B": 100.0})
        assert result == {"A": 50.0, "B": 50.0}
    
    def test_close_positions(self):
        """Test with very close positions."""
        result = compute_vote_shares({"A": 49.9, "B": 50.0, "C": 50.1})
        # Midpoints: 49.95, 50.05
        # A: 0-49.95 = 49.95%, B: 49.95-50.05 = 0.1%, C: 50.05-100 = 49.95%
        assert abs(result["A"] - 49.95) < 0.001
        assert abs(result["B"] - 0.1) < 0.001
        assert abs(result["C"] - 49.95) < 0.001


class TestVoteResult:
    """Test cases for the VoteResult class."""
    
    def test_vote_result_init(self):
        """Test VoteResult initialization."""
        positions = {"A": 30.0, "B": 70.0}
        result = VoteResult(positions)
        
        assert result.positions == positions
        assert result.shares == {"A": 50.0, "B": 50.0}
        assert result.total_options == 2
    
    def test_get_sorted_results(self):
        """Test getting sorted results."""
        positions = {"C": 80.0, "A": 20.0, "B": 50.0}
        result = VoteResult(positions)
        
        sorted_results = result.get_sorted_results()
        
        # Should be sorted by position
        assert len(sorted_results) == 3
        assert sorted_results[0][0] == "A"  # position 20.0
        assert sorted_results[1][0] == "B"  # position 50.0
        assert sorted_results[2][0] == "C"  # position 80.0
        
        # Check shares are correct
        assert sorted_results[0][2] == 35.0  # A's share
        assert sorted_results[1][2] == 30.0  # B's share
        assert sorted_results[2][2] == 35.0  # C's share


if __name__ == "__main__":
    pytest.main([__file__])