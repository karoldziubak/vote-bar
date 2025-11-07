"""
Core voting logic for the vote-bar system.

This module implements the "100% bar" voting concept using 1D Voronoi diagram logic.
Users select options and assign positions (0-100). Each option's share is determined
by the territory it controls based on midpoints between adjacent positions.
"""

from typing import Dict, List, Tuple


def compute_vote_shares(positions: Dict[str, float]) -> Dict[str, float]:
    """
    Given option:position pairs (0–100), return option:share percentages summing to 100%.
    
    Uses 1D Voronoi diagram logic: each option controls territory from the midpoint
    to its nearest neighbors on each side.
    
    Args:
        positions: Dictionary mapping option names to their positions (0.0 to 100.0)
        
    Returns:
        Dictionary mapping option names to their percentage shares (0.0 to 100.0)
        
    Examples:
        >>> compute_vote_shares({"A": 50.0})
        {"A": 100.0}
        
        >>> compute_vote_shares({"A": 30.0, "B": 70.0})
        {"A": 50.0, "B": 50.0}
        
        >>> compute_vote_shares({"A": 20.0, "B": 50.0, "C": 80.0})
        {"A": 35.0, "B": 30.0, "C": 35.0}
    """
    if not positions:
        return {}
    
    if len(positions) == 1:
        # Single option gets 100%
        option_name = list(positions.keys())[0]
        return {option_name: 100.0}
    
    # Sort options by their positions
    sorted_options = sorted(positions.items(), key=lambda x: x[1])
    shares = {}
    
    for i, (option_name, position) in enumerate(sorted_options):
        left_boundary = 0.0
        right_boundary = 100.0
        
        # Calculate left boundary (midpoint with previous option)
        if i > 0:
            prev_position = sorted_options[i - 1][1]
            left_boundary = (prev_position + position) / 2.0
        
        # Calculate right boundary (midpoint with next option)
        if i < len(sorted_options) - 1:
            next_position = sorted_options[i + 1][1]
            right_boundary = (position + next_position) / 2.0
        
        # Territory share is the width of this option's segment
        territory_width = right_boundary - left_boundary
        shares[option_name] = territory_width
    
    return shares


# Simple data class for storing vote results (optional, for future use)
class VoteResult:
    """Simple container for vote results."""
    
    def __init__(self, positions: Dict[str, float]):
        self.positions = positions
        self.shares = compute_vote_shares(positions)
        self.total_options = len(positions)
    
    def get_sorted_results(self) -> List[Tuple[str, float, float]]:
        """Return results sorted by position: (option, position, share)"""
        return sorted(
            [(opt, self.positions[opt], self.shares[opt]) for opt in self.positions],
            key=lambda x: x[1]  # Sort by position
        )