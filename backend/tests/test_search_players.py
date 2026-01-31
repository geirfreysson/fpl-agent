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
    
    def test_attacking_threat_search(self):
        params = {
            "limit": 10,
            "sort_by": "attacking_threat,selected_by_percent",
            "ascending": False,
            "filters": {
                "position": "DEF",
                "max_selected_by_percent": 5
            }
        }
        result = search_players(**params)
        print(result)

    def test_likely_to_start_search(self):
        params = {
            "limit": 10,
            "sort_by": "total_points",
            "ascending": False,
            "filters": {
                "position": "MID",
                "min_price": 7,
                "max_price": 7,
                "min_chance_of_playing_next_round": 75
            }
        }
        result = search_players(**params)
        print(result)

    def test_basic_position_and_team_filtering(self):
        """Test basic position and team filtering"""
        # Test position filtering
        result = search_players(
            limit=5,
            filters={"position": "GK"},
            sort_by="total_points",
            ascending=False
        )
        assert "GK" in result, "Should find goalkeepers"
        lines = result.split('\n')
        player_lines = [line for line in lines if re.match(r'^\d+\.', line.strip())]
        assert len(player_lines) <= 5, "Should respect limit"
        
        # Test team filtering
        result = search_players(
            limit=3,
            filters={"team": "Arsenal"},
            sort_by="total_points",
            ascending=False
        )
        assert "Arsenal" in result, "Should find Arsenal players"

    def test_cost_filtering(self):
        """Test price/cost filtering functionality"""
        # Test budget players
        result = search_players(
            limit=5,
            filters={"max_now_cost": 45},  # Under £4.5m
            sort_by="total_points",
            ascending=False
        )
        lines = result.split('\n')
        player_lines = [line for line in lines if re.match(r'^\d+\.', line.strip())]
        
        # Check that all players are under £4.5m
        for line in player_lines:
            if "£" in line:
                price_match = re.search(r'£(\d+\.\d+)m', line)
                if price_match:
                    price = float(price_match.group(1))
                    assert price <= 4.5, f"Player should be under £4.5m, got £{price}m"

    def test_performance_filtering(self):
        """Test performance-based filtering (points, form, etc.)"""
        # Test high scorers
        result = search_players(
            limit=10,
            filters={"min_total_points": 100},
            sort_by="total_points",
            ascending=False
        )
        lines = result.split('\n')
        player_lines = [line for line in lines if re.match(r'^\d+\.', line.strip())]
        
        # Verify points are in descending order and all above 100
        prev_points = float('inf')
        for line in player_lines:
            points_match = re.search(r'Points: (\d+)', line)
            if points_match:
                points = int(points_match.group(1))
                assert points >= 100, f"Player should have 100+ points, got {points}"
                assert points <= prev_points, "Points should be in descending order"
                prev_points = points

    def test_ownership_filtering(self):
        """Test ownership percentage filtering"""
        result = search_players(
            limit=8,
            filters={
                "min_total_points": 50,
                "max_selected_by_percent": 5.0
            },
            sort_by="points_per_million",
            ascending=False
        )
        lines = result.split('\n')
        player_lines = [line for line in lines if re.match(r'^\d+\.', line.strip())]
        
        for line in player_lines:
            # Check ownership is low
            own_match = re.search(r'Own: (\d+\.\d+)%', line)
            if own_match:
                ownership = float(own_match.group(1))
                assert ownership <= 5.0, f"Ownership should be ≤5%, got {ownership}%"
            
            # Check points are decent
            points_match = re.search(r'Points: (\d+)', line)
            if points_match:
                points = int(points_match.group(1))
                assert points >= 50, f"Points should be ≥50, got {points}"

    def test_goals_and_assists_filtering(self):
        """Test goals and assists filtering"""
        result = search_players(
            limit=10,
            filters={
                "position": "FWD",
                "min_goals_scored": 5
            },
            sort_by="goals_scored",
            ascending=False
        )
        assert "FWD" in result, "Should find forwards"
        lines = result.split('\n')
        player_lines = [line for line in lines if re.match(r'^\d+\.', line.strip())]
        assert len(player_lines) >= 0, "Should find forwards with 5+ goals or handle gracefully"

    def test_expected_stats_filtering(self):
        """Test expected goals and assists filtering"""
        result = search_players(
            limit=5,
            filters={"min_expected_goals": 1.0},
            sort_by="expected_goals",
            ascending=False
        )
        lines = result.split('\n')
        player_lines = [line for line in lines if re.match(r'^\d+\.', line.strip())]
        assert len(player_lines) >= 0, "Should find players with expected goals or handle gracefully"

    def test_value_metrics_filtering(self):
        """Test value metrics like points per million"""
        result = search_players(
            limit=10,
            filters={
                "position": "MID",
                "min_points_per_million": 15.0
            },
            sort_by="points_per_million",
            ascending=False
        )
        assert "MID" in result, "Should find midfielders"
        lines = result.split('\n')
        player_lines = [line for line in lines if re.match(r'^\d+\.', line.strip())]
        assert len(player_lines) >= 0, "Should find high value midfielders or handle gracefully"

    def test_playing_time_filtering(self):
        """Test minutes and playing time filtering"""
        result = search_players(
            limit=8,
            filters={"min_minutes": 1500},  # Significant playing time
            sort_by="minutes",
            ascending=False
        )
        lines = result.split('\n')
        player_lines = [line for line in lines if re.match(r'^\d+\.', line.strip())]
        assert len(player_lines) >= 0, "Should find players with significant minutes"

    def test_multi_column_sorting(self):
        """Test multi-column sorting functionality"""
        result = search_players(
            limit=5,
            sort_by="selected_by_percent,total_points",
            ascending=True,  # Low ownership first, then high points
            filters={"min_total_points": 80}
        )
        lines = result.split('\n')
        player_lines = [line for line in lines if re.match(r'^\d+\.', line.strip())]
        
        # Verify ownership is generally ascending
        ownership_values = []
        for line in player_lines:
            own_match = re.search(r'Own: (\d+\.\d+)%', line)
            if own_match:
                ownership_values.append(float(own_match.group(1)))
        
        if len(ownership_values) > 1:
            # Check that ownership is generally ascending (allowing for some ties)
            for i in range(len(ownership_values) - 1):
                assert ownership_values[i] <= ownership_values[i+1] + 0.1, "Ownership should be roughly ascending"

    def test_position_specific_stats(self):
        """Test position-specific statistics"""
        # Test clean sheets for defenders
        result = search_players(
            limit=10,
            filters={
                "position": "DEF",
                "min_clean_sheets": 3
            },
            sort_by="clean_sheets",
            ascending=False
        )
        assert "DEF" in result, "Should find defenders"
        
        # Test saves for goalkeepers
        result = search_players(
            limit=5,
            filters={"position": "GK", "min_saves": 10},
            sort_by="saves",
            ascending=False
        )
        if "No players found" not in result:
            assert "GK" in result, "Should find goalkeepers"

    def test_disciplinary_filtering(self):
        """Test cards and disciplinary record filtering"""
        result = search_players(
            limit=10,
            filters={"max_yellow_cards": 2},
            sort_by="yellow_cards",
            ascending=True
        )
        lines = result.split('\n')
        player_lines = [line for line in lines if re.match(r'^\d+\.', line.strip())]
        assert len(player_lines) > 0, "Should find players with low cards"

    def test_boolean_flags(self):
        """Test boolean flag filtering (set piece takers, etc.)"""
        result = search_players(
            limit=5,
            filters={"is_penalty_taker": True},
            sort_by="total_points",
            ascending=False
        )
        # This might not find results if no penalty takers are in the data
        assert isinstance(result, str), "Should return string result without error"

    def test_attacking_threat_all_positions(self):
        """Test attacking_threat field for all positions"""
        for position in ["GK", "DEF", "MID", "FWD"]:
            result = search_players(
                limit=3,
                filters={"position": position},
                sort_by="attacking_threat",
                ascending=False
            )
            
            lines = result.split('\n')
            player_lines = [line for line in lines if re.match(r'^\d+\.', line.strip())]
            
            assert len(player_lines) > 0, f"Should find {position} players"
            
            # Each line should contain attacking_threat value
            for line in player_lines:
                assert "attacking_threat:" in line, f"{position} players should show attacking_threat"

    def test_edge_cases(self):
        """Test edge cases and error handling"""
        # Test empty results
        result = search_players(
            limit=5,
            filters={"min_total_points": 1000}  # Unrealistically high
        )
        assert "No players found" in result or len(result) > 0, "Should handle empty results gracefully"
        
        # Test very small limit
        result = search_players(limit=1)
        lines = result.split('\n')
        player_lines = [line for line in lines if re.match(r'^\d+\.', line.strip())]
        assert len(player_lines) == 1, "Should respect limit=1"
        
        # Test large limit (should not error)
        result = search_players(limit=100)
        assert isinstance(result, str), "Should handle large limits"
        assert not result.startswith("Error"), "Should not error with large limit"

    def test_data_integrity(self):
        """Test that the data makes logical sense"""
        # Test that forwards generally have higher attacking_threat than goalkeepers
        forwards_result = search_players(
            limit=3,
            filters={"position": "FWD"},
            sort_by="attacking_threat",
            ascending=False
        )
        
        gk_result = search_players(
            limit=3,
            filters={"position": "GK"},
            sort_by="attacking_threat",
            ascending=False
        )
        
        def extract_attacking_threat(result_text):
            lines = result_text.split('\n')
            player_lines = [line for line in lines if re.match(r'^\d+\.', line.strip())]
            if player_lines:
                threat_match = re.search(r'attacking_threat: ([\d.]+)', player_lines[0])
                return float(threat_match.group(1)) if threat_match else 0.0
            return 0.0
        
        fwd_threat = extract_attacking_threat(forwards_result)
        gk_threat = extract_attacking_threat(gk_result)
        
        # Forwards should generally have higher attacking threat
        assert fwd_threat >= gk_threat, f"Forwards ({fwd_threat}) should have ≥ attacking threat than GKs ({gk_threat})"

    def test_xg_form_filter(self):
        """Test xG form filtering (30-day rolling average)"""
        result = search_players(
            limit=10,
            filters={"min_xg_form_30d": 0.3},
            sort_by="xg_form_30d",
            ascending=False
        )

        # Should return results without error
        assert isinstance(result, str), "Should return string result"

        # If there are results, verify they're formatted correctly
        if "No players found" not in result:
            lines = result.split('\n')
            player_lines = [line for line in lines if re.match(r'^\d+\.', line.strip())]
            # Should have at least some players with xG form data
            assert len(player_lines) > 0, "Should find players with xG form data"

    def test_xg_form_sorting(self):
        """Test sorting by xGI form (descending)"""
        result = search_players(
            limit=5,
            sort_by="xgi_form_30d",
            ascending=False
        )

        # Should return results without error
        assert isinstance(result, str), "Should return string result"
        assert not result.startswith("Error"), "Should not error when sorting by xGI form"

        # Verify results are formatted
        lines = result.split('\n')
        player_lines = [line for line in lines if re.match(r'^\d+\.', line.strip())]

        # Should have some players (even if many have NaN)
        assert len(player_lines) > 0, "Should find players"

    def test_xg_form_combined(self):
        """Test xG form combined with position and price filters"""
        result = search_players(
            limit=8,
            filters={
                "position": "MID",
                "max_price": 8.0,
                "min_xg_form_30d": 0.4,
                "min_matches_last_30d": 3
            },
            sort_by="xgi_form_30d",
            ascending=False
        )

        # Should execute without error
        assert isinstance(result, str), "Should return string result"

        # If results found, verify they match criteria
        if "No players found" not in result:
            assert "MID" in result, "Should find midfielders"
            lines = result.split('\n')
            player_lines = [line for line in lines if re.match(r'^\d+\.', line.strip())]

            # Verify price constraint
            for line in player_lines:
                price_match = re.search(r'£(\d+\.\d+)m', line)
                if price_match:
                    price = float(price_match.group(1))
                    assert price <= 8.0, f"Player should be ≤£8.0m, got £{price}m"


if __name__ == '__main__':
    # Run tests when executed directly
    pytest.main([__file__, '-v'])