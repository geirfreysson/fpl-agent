#!/usr/bin/env python3
"""
Test suite for the search_players function
"""

import pytest
import sys
import os
import re

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tools import search_players


class TestSearchPlayers:
    """Test cases for search_players function"""
    
    def test_basic_limit_functionality(self):
        """Test that limit parameter works correctly"""
        result = search_players(limit=5, sort_by='total_points', ascending=False)
        
        # Count player lines (lines with ". " pattern and not header)
        lines = result.split('\n')
        player_lines = [line for line in lines if re.match(r'^\d+\.', line.strip())]
        
        assert len(player_lines) == 5, f"Expected 5 players, got {len(player_lines)}"
    
    def test_goal_keepers_max_price(self):
        """Test that max_price parameter works correctly for goalkeepers"""
        params = {'filters': {'position': 'GK', 'max_price': 4.5}, 'sort_by': 'total_points', 'ascending': False, 'limit': 5}  
        result = search_players(**params)
        
        # Count player lines (lines with ". " pattern and not header)
        lines = result.split('\n')
        player_lines = [line for line in lines if re.match(r'^\d+\.', line.strip())]
        print(result)
        assert len(player_lines) == 5, f"Expected 5 players, got {len(player_lines)}"

    def test_limit_10_returns_10_results(self):
        """Test that limit=10 returns exactly 10 results"""
        result = search_players(limit=10, sort_by='total_points', ascending=False)
        
        lines = result.split('\n')
        player_lines = [line for line in lines if re.match(r'^\d+\.', line.strip())]
        
        assert len(player_lines) == 10, f"Expected 10 players, got {len(player_lines)}"
    



if __name__ == '__main__':
    # Run tests when executed directly
    pytest.main([__file__, '-v'])