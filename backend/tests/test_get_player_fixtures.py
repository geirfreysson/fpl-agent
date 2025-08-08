#!/usr/bin/env python3
"""
Test suite for the get_player_fixtures function
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tools import get_player_fixtures


class TestGetPlayerFixtures:
    """Test cases for get_player_fixtures function"""
    
    def test_multiple_players_fixtures(self):
        """Test fixture analysis for multiple players from the provided list"""
        players = "J. Murphy,Iwobi,Sarr,Mitoma,Szoboszlai,Enzo,Bruno G.,Damsgaard,Barnes,Amad"
        result = get_player_fixtures(players)
        
        # Basic validation - should return a string
        assert isinstance(result, str), f"Expected string result, got {type(result)}"
        assert len(result) > 0, "Result should not be empty"
        
        # Should contain the header
        assert "Player Fixture Analysis" in result, "Should contain analysis header"
        
        # Should contain some player names (at least some should be found)
        found_any_player = any(name in result for name in ["Murphy", "Iwobi", "Sarr", "Mitoma", "Szoboszlai"])
        assert found_any_player, "Should find at least some players from the list"
        
        # Should contain fixture difficulty information
        assert "Average Fixture Difficulty" in result, "Should contain average difficulty"
        assert "Upcoming Fixtures" in result, "Should contain upcoming fixtures"
        
        # Should contain venue information (H) or (A)
        assert "(H)" in result or "(A)" in result, "Should contain venue information"
        
        # Should contain difficulty ratings
        assert "Difficulty:" in result, "Should contain difficulty ratings"
        
        print("Test result:")
        print(result)


if __name__ == '__main__':
    # Run tests when executed directly
    pytest.main([__file__, '-v'])