"""
Core voting logic for the vote-bar system.

This module implements the "100% bar" voting concept where users
can drag and drop option icons onto a bar to express preferences.
The position of icons on the bar determines the percentage allocation.
"""

from typing import Dict, List, Tuple
import pandas as pd


class PositionVote:
    """
    Represents a single vote with option positions on the bar.
    
    Positions are stored as (start_position, end_position) tuples
    where positions are percentages (0.0 to 100.0) along the bar.
    """
    
    def __init__(self, option_positions: Dict[str, Tuple[float, float]]):
        """
        Initialize a position-based vote.
        
        Args:
            option_positions: Dict mapping option names to (start, end) position tuples
        """
        self.option_positions = option_positions
        self.percentages = self._calculate_percentages()
    
    def _calculate_percentages(self) -> Dict[str, float]:
        """Calculate percentage allocation from positions."""
        percentages = {}
        for option, (start, end) in self.option_positions.items():
            percentages[option] = abs(end - start)
        return percentages


class VoteBar:
    """
    Represents a voting session using the drag-and-drop 100% bar concept.
    
    Users drag option icons onto a bar. The positions determine 
    the percentage allocation across options.
    """
    
    def __init__(self, options: List[str]):
        """
        Initialize a new voting session.
        
        Args:
            options: List of voting options available to users
        """
        self.options = options
        self.votes: List[PositionVote] = []
    
    def add_position_vote(self, option_positions: Dict[str, Tuple[float, float]]) -> bool:
        """
        Add a new position-based vote to the session.
        
        Args:
            option_positions: Dict mapping option names to (start, end) position tuples
            
        Returns:
            True if vote is valid and added, False otherwise
        """
        if not self._validate_positions(option_positions):
            return False
        
        position_vote = PositionVote(option_positions)
        self.votes.append(position_vote)
        return True
    
    def add_vote(self, vote: Dict[str, float]) -> bool:
        """
        Add a traditional percentage-based vote (for backward compatibility).
        
        Args:
            vote: Dictionary mapping option names to percentage allocations
            
        Returns:
            True if vote is valid and added, False otherwise
        """
        if not self._validate_vote(vote):
            return False
        
        # Convert percentage vote to position vote
        position = 0.0
        option_positions = {}
        
        for option in self.options:
            percentage = vote.get(option, 0.0)
            if percentage > 0:
                option_positions[option] = (position, position + percentage)
                position += percentage
        
        position_vote = PositionVote(option_positions)
        self.votes.append(position_vote)
        return True
    
    def _validate_positions(self, option_positions: Dict[str, Tuple[float, float]]) -> bool:
        """
        Validate position-based vote data.
        
        Args:
            option_positions: Positions to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check if all options are valid
        if not all(option in self.options for option in option_positions.keys()):
            return False
        
        # Check if positions are valid (0-100 range)
        for start, end in option_positions.values():
            if not (0 <= start <= 100 and 0 <= end <= 100):
                return False
        
        # Check for overlapping positions
        positions = list(option_positions.values())
        for i, (start1, end1) in enumerate(positions):
            for j, (start2, end2) in enumerate(positions[i+1:], i+1):
                # Check if ranges overlap
                if not (end1 <= start2 or end2 <= start1):
                    return False
        
        return True
    
    def _validate_vote(self, vote: Dict[str, float]) -> bool:
        """
        Validate traditional percentage-based vote (backward compatibility).
        
        Args:
            vote: Vote to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check if all options in vote are valid
        if not all(option in self.options for option in vote.keys()):
            return False
        
        # Check if percentages sum to 100 (with small tolerance for floating point)
        total = sum(vote.values())
        if abs(total - 100.0) > 0.01:
            return False
        
        # Check if all percentages are non-negative
        if any(value < 0 for value in vote.values()):
            return False
        
        return True
    
    def get_results(self) -> pd.DataFrame:
        """
        Calculate and return voting results from position-based votes.
        
        Returns:
            DataFrame with options and their average scores
        """
        if not self.votes:
            return pd.DataFrame(columns=['option', 'average_score', 'total_votes'])
        
        # Calculate average scores for each option
        results = []
        for option in self.options:
            scores = []
            for vote in self.votes:
                if isinstance(vote, PositionVote):
                    scores.append(vote.percentages.get(option, 0.0))
                else:
                    # Backward compatibility for old-style votes
                    scores.append(vote.get(option, 0.0))
            
            avg_score = sum(scores) / len(self.votes)
            total_votes = sum(1 for score in scores if score > 0)
            
            results.append({
                'option': option,
                'average_score': avg_score,
                'total_votes': total_votes
            })
        
        return pd.DataFrame(results).sort_values('average_score', ascending=False)
    
    def get_position_summary(self) -> Dict[str, List[Tuple[float, float]]]:
        """
        Get a summary of all positions for each option across all votes.
        
        Returns:
            Dict mapping option names to lists of (start, end) position tuples
        """
        position_summary = {option: [] for option in self.options}
        
        for vote in self.votes:
            if isinstance(vote, PositionVote):
                for option, position in vote.option_positions.items():
                    position_summary[option].append(position)
        
        return position_summary