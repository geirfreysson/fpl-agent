#!/usr/bin/env python3
"""
Test suite for other FPL tools
"""

import pytest
import sys
import os
import re

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tools import (
    get_players_by_price_range,
    get_player_fixtures,
    get_player_form,
    find_player_replacements,
    get_easiest_fixtures,
    help
)


class TestFPLTools:
    """Test cases for various FPL analysis tools"""
    
    def test_get_players_by_price_range_basic(self):
        """Test basic price range functionality"""
        result = get_players_by_price_range(min_price=4.0, max_price=6.0)
        
        assert "Players in price range £4.0m - £6.0m" in result
        
        # Should contain some players
        lines = result.split('\n')
        player_lines = [line for line in lines if re.match(r'^\d+\.', line.strip())]
        assert len(player_lines) > 0, "Should find some players in price range"
        
        # Verify prices are in range
        for line in player_lines:
            price_match = re.search(r'£(\d+\.\d+)m', line)
            if price_match:
                price = float(price_match.group(1))
                assert 4.0 <= price <= 6.0, f"Price {price} not in range 4.0-6.0"
    
    def test_get_players_by_price_range_with_position(self):
        """Test price range with position filter"""
        result = get_players_by_price_range(
            min_price=8.0, 
            max_price=12.0, 
            position='midfielder'
        )
        
        assert "Midfielders in price range £8.0m - £12.0m" in result
        
        lines = result.split('\n')
        player_lines = [line for line in lines if re.match(r'^\d+\.', line.strip())]
        
        # All should be midfielders
        for line in player_lines:
            assert '(MID)' in line, f"Expected MID position in line: {line}"
    
    def test_get_player_fixtures_single_player(self):
        """Test fixture analysis for a single player"""
        result = get_player_fixtures("Salah", num_fixtures=3)
        
        assert "Fixture Analysis" in result
        assert "Salah" in result or "not found" in result.lower()
        
        if "not found" not in result.lower():
            # Should show fixtures
            assert "vs" in result or "Fixtures:" in result
    
    def test_get_player_fixtures_multiple_players(self):
        """Test fixture analysis for multiple players"""
        result = get_player_fixtures("Salah, Haaland", num_fixtures=5)
        
        assert "Fixture Analysis" in result
        # Should mention both players or indicate they weren't found
        lines = result.split('\n')
        assert len(lines) > 3, "Should have substantial content for multiple players"
    
    def test_get_player_form_single_player(self):
        """Test form analysis for a single player"""
        result = get_player_form("Salah")
        
        assert "Player Form Analysis" in result
        assert "Salah" in result or "not found" in result.lower()
        
        if "not found" not in result.lower():
            # Should contain form metrics
            assert any(word in result.lower() for word in ['form', 'points', 'performance'])
    
    def test_get_player_form_multiple_players(self):
        """Test form analysis for multiple players"""
        result = get_player_form("Salah, Haaland, Son")
        
        assert "Player Form Analysis" in result
        lines = result.split('\n')
        assert len(lines) > 3, "Should have content for multiple players"
    
    def test_get_player_form_detailed(self):
        """Test detailed form analysis"""
        result = get_player_form("Salah", detailed=True)
        
        assert "Player Form Analysis" in result
        # Detailed mode should have more content
        lines = result.split('\n')
        assert len(lines) > 5, "Detailed analysis should have more lines"
    
    def test_find_player_replacements(self):
        """Test player replacement suggestions"""
        result = find_player_replacements("Salah", price_tolerance=2.0, max_suggestions=3)
        
        assert "Player Replacement Analysis" in result
        assert "Salah" in result or "not found" in result.lower()
        
        if "not found" not in result.lower():
            # Should have replacement suggestions
            assert "Position:" in result
            assert "Price:" in result
    
    def test_find_player_replacements_tight_budget(self):
        """Test player replacements with tight budget"""
        result = find_player_replacements("Haaland", price_tolerance=0.5, max_suggestions=2)
        
        assert "Player Replacement Analysis" in result
        # Should either find replacements or indicate limited options
        assert len(result) > 50, "Should have substantial content"
    
    def test_get_easiest_fixtures_default(self):
        """Test easiest fixtures with default parameters"""
        result = get_easiest_fixtures()
        
        assert "Easiest Fixtures Analysis" in result or "Teams with Easiest Fixtures" in result
        
        lines = result.split('\n')
        assert len(lines) > 3, "Should have multiple lines of fixture analysis"
        
        # Should mention teams and difficulty
        content_lower = result.lower()
        assert any(word in content_lower for word in ['team', 'difficulty', 'fixture'])
    
    def test_get_easiest_fixtures_custom_number(self):
        """Test easiest fixtures with custom number"""
        result = get_easiest_fixtures(num_fixtures=5)
        
        assert "5" in result or "five" in result.lower()
        assert len(result) > 30, "Should have substantial content"
    
    def test_help_function(self):
        """Test help function returns useful information"""
        result = help()
        
        assert len(result) > 100, "Help should be substantial"
        
        # Should contain information about available functions
        content_lower = result.lower()
        assert any(word in content_lower for word in [
            'search', 'player', 'fixture', 'form', 'price', 'help'
        ])
    
    def test_invalid_player_name(self):
        """Test handling of invalid player names"""
        result = get_player_form("NonExistentPlayer123")
        
        assert "not found" in result.lower() or "no players" in result.lower()
    
    def test_edge_case_empty_player_name(self):
        """Test handling of empty player name"""
        result = get_player_form("")
        
        # Should handle gracefully
        assert len(result) > 10, "Should return some response for empty input"
    
    def test_price_range_invalid_range(self):
        """Test invalid price range (min > max)"""
        result = get_players_by_price_range(min_price=10.0, max_price=5.0)
        
        # Should either handle gracefully or return no results
        assert len(result) > 10, "Should return some response"
    
    def test_fixtures_zero_number(self):
        """Test fixtures with zero number"""
        result = get_easiest_fixtures(num_fixtures=0)
        
        # Should handle gracefully
        assert len(result) > 10, "Should return some response for zero fixtures"
    
    @pytest.mark.parametrize("position", ["goalkeeper", "defender", "midfielder", "forward"])
    def test_price_range_all_positions(self, position):
        """Test price range for all valid positions"""
        result = get_players_by_price_range(
            min_price=4.0, 
            max_price=8.0, 
            position=position
        )
        
        assert f"{position.title()}s" in result or position.upper()[:3] in result
        assert len(result) > 20, f"Should have content for {position}"


if __name__ == '__main__':
    # Run tests when executed directly
    pytest.main([__file__, '-v'])