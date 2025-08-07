#!/usr/bin/env python3
"""
Test suite for the get_player_details function
"""

import pytest
import sys
import os
import re

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tools import get_player_details


class TestGetPlayerDetails:
    """Test cases for get_player_details function"""
    
    def test_morgan_rogers_details(self):
        """Test get_player_details with Morgan Rogers"""
        result = get_player_details("Morgan Rogers")
        print("Morgan Rogers details:")
        print(result)
        
        # Basic assertions
        assert isinstance(result, str), "Should return string result"
        assert not result.startswith("Error"), "Should not return error"
        
        # The function returns structured data, not necessarily the player name
        # Instead check for expected data patterns for Morgan Rogers (Aston Villa midfielder)
        assert "Aston Villa" in result, "Morgan Rogers should be from Aston Villa"
        assert "MID" in result, "Morgan Rogers should be a midfielder"
        
        # Check for required sections in the markdown output
        expected_sections = [
            "## Basic Info",
            "## Season Statistics", 
            "## Value Analysis",
            "## Performance Metrics",
            "## ICT Index Breakdown",
            "## Disciplinary",
            "## Availability"
        ]
        
        for section in expected_sections:
            assert section in result, f"Should contain {section} section"
        
        # Check for key data points
        assert "Team" in result, "Should show team information"
        assert "Position" in result, "Should show position"
        assert "Price" in result, "Should show price"
        assert "Total Points" in result, "Should show total points"
        assert "Ownership" in result, "Should show ownership percentage"
        
        print(f"✅ Morgan Rogers details test passed")
        print(f"Result length: {len(result)} characters")
        
    def test_player_details_data_integrity(self):
        """Test that player details contain logical data"""
        result = get_player_details("Morgan Rogers")
        
        if not result.startswith("Error") and "not found" not in result.lower():
            # Extract position from the result
            position_match = re.search(r'\| Position\s+\| (\w+)', result)
            if position_match:
                position = position_match.group(1)
                assert position in ["GK", "DEF", "MID", "FWD"], f"Position should be valid: {position}"
            
            # Extract price and verify it's reasonable
            price_match = re.search(r'\| Price\s+\| £([\d.]+)m', result)
            if price_match:
                price = float(price_match.group(1))
                assert 3.5 <= price <= 15.0, f"Price should be reasonable: £{price}m"
            
            # Check that ownership is a valid percentage
            ownership_match = re.search(r'\| Ownership\s+\| ([\d.]+)%', result)
            if ownership_match:
                ownership = float(ownership_match.group(1))
                assert 0 <= ownership <= 100, f"Ownership should be valid percentage: {ownership}%"
        
        print("✅ Data integrity test passed")
    
    def test_player_not_found(self):
        """Test behavior when player is not found"""
        result = get_player_details("NonexistentPlayerName123")
        
        assert isinstance(result, str), "Should return string result"
        assert ("not found" in result.lower() or 
                result.startswith("❌")), "Should indicate player not found"
        
        print("✅ Player not found test passed")
    
    def test_partial_name_matching(self):
        """Test that partial name matching works"""
        # Test with just "Rogers" - should find Morgan Rogers
        result = get_player_details("Rogers")
        
        assert isinstance(result, str), "Should return string result"
        if not result.startswith("Error") and "not found" not in result.lower():
            # If it finds a player, it should contain player info
            assert "Team" in result, "Should contain team info if player found"
            assert "Position" in result, "Should contain position if player found"
        
        print("✅ Partial name matching test passed")
    
    def test_case_insensitive_search(self):
        """Test that case insensitive search works"""
        result1 = get_player_details("morgan rogers")  # lowercase
        result2 = get_player_details("MORGAN ROGERS")  # uppercase
        result3 = get_player_details("Morgan Rogers")  # proper case
        
        # All should return similar results (either all found or all not found)
        all_found = all(not r.startswith("Error") and "not found" not in r.lower() 
                       for r in [result1, result2, result3])
        all_not_found = all("not found" in r.lower() or r.startswith("❌") 
                          for r in [result1, result2, result3])
        
        assert all_found or all_not_found, "Case sensitivity should be consistent"
        
        print("✅ Case insensitive search test passed")
    
    def test_result_format_structure(self):
        """Test that the result has proper markdown structure"""
        result = get_player_details("Morgan Rogers")
        
        if not result.startswith("Error") and "not found" not in result.lower():
            # Check markdown table structure
            assert "|" in result, "Should contain markdown table pipes"
            assert "Metric" in result, "Should contain Metric column header"
            assert "Value" in result, "Should contain Value column header"
            
            # Count number of sections (should be multiple)
            section_count = result.count("##")
            assert section_count >= 5, f"Should have multiple sections, got {section_count}"
            
            # Verify no broken markdown
            lines = result.split('\n')
            table_lines = [line for line in lines if '|' in line and line.strip()]
            if table_lines:
                # Each table line should have consistent pipe count
                pipe_counts = [line.count('|') for line in table_lines[:5]]  # Check first 5 table lines
                if len(set(pipe_counts)) > 1:  # If pipe counts vary significantly
                    print(f"Warning: Inconsistent table structure - pipe counts: {pipe_counts}")
        
        print("✅ Result format structure test passed")
    
    def test_tier_classification(self):
        """Test that tier classification is present and reasonable"""
        result = get_player_details("Morgan Rogers")
        
        if not result.startswith("Error") and "not found" not in result.lower():
            # Should contain tier information
            tier_indicators = ["ELITE", "PREMIUM", "SOLID", "DECENT", "BUDGET", "BENCH"]
            has_tier = any(indicator in result for indicator in tier_indicators)
            assert has_tier, "Should contain tier classification"
            
            # Should have emoji indicators
            tier_emojis = ["🏆", "⭐", "📈", "📊", "⚠️"]
            has_emoji = any(emoji in result for emoji in tier_emojis)
            assert has_emoji, "Should contain tier emoji"
        
        print("✅ Tier classification test passed")
    
    def test_salah_details(self):
        """Test get_player_details with Mohamed Salah"""
        result = get_player_details("Salah")
        print("Salah details found")
        
        # Basic assertions
        assert isinstance(result, str), "Should return string result"
        assert not result.startswith("Error"), "Should not return error"
        
        # Mohamed Salah should be Liverpool forward with high points
        assert "Liverpool" in result, "Salah should be from Liverpool"
        assert ("FWD" in result or "MID" in result), "Salah should be FWD or MID"
        
        # Should have high points (one of the top scorers)
        if "Total Points" in result:
            # Extract points to verify it's reasonably high for a premium player
            import re
            points_match = re.search(r'Total Points\s+\|\s+(\d+)', result)
            if points_match:
                points = int(points_match.group(1))
                assert points >= 100, f"Salah should have high points, got {points}"

    def test_haaland_details(self):
        """Test get_player_details with Erling Haaland"""
        result = get_player_details("Haaland")
        print("Haaland details found")
        
        # Basic assertions
        assert isinstance(result, str), "Should return string result"
        assert not result.startswith("Error"), "Should not return error"
        
        # Haaland should be Manchester City forward
        assert "Man City" in result, "Haaland should be from Manchester City"
        assert "FWD" in result, "Haaland should be a forward"
        
        # Should be expensive (premium player)
        if "Price" in result:
            import re
            price_match = re.search(r'Price\s+\|\s+£([\d.]+)m', result)
            if price_match:
                price = float(price_match.group(1))
                assert price >= 10.0, f"Haaland should be expensive, got £{price}m"

    def test_palmer_details(self):
        """Test get_player_details with Cole Palmer"""
        result = get_player_details("Palmer")
        print("Palmer details found")
        
        # Basic assertions
        assert isinstance(result, str), "Should return string result"
        assert not result.startswith("Error"), "Should not return error"
        
        # Cole Palmer should be Chelsea midfielder/forward
        assert "Chelsea" in result, "Palmer should be from Chelsea"
        assert ("MID" in result or "FWD" in result), "Palmer should be MID or FWD"

    def test_van_dijk_details(self):
        """Test get_player_details with Virgil van Dijk (hyphenated name)"""
        result = get_player_details("van Dijk")
        print("van Dijk details found")
        
        # Basic assertions
        assert isinstance(result, str), "Should return string result"
        assert not result.startswith("Error"), "Should not return error"
        
        # van Dijk should be Liverpool defender
        assert "Liverpool" in result, "van Dijk should be from Liverpool"
        assert "DEF" in result, "van Dijk should be a defender"

    def test_foden_details(self):
        """Test get_player_details with Phil Foden (Man City midfielder)"""
        result = get_player_details("Foden")
        print("Foden details found")
        
        # Basic assertions
        assert isinstance(result, str), "Should return string result"
        assert not result.startswith("Error"), "Should not return error"
        
        # Foden should be Manchester City midfielder
        assert "Man City" in result, "Foden should be from Manchester City"
        assert "MID" in result, "Foden should be a midfielder"

    def test_son_heung_min_details(self):
        """Test get_player_details with Son Heung-min (Korean name)"""
        result = get_player_details("Son")
        print("Son details found")
        
        # Basic assertions
        assert isinstance(result, str), "Should return string result"
        assert not result.startswith("Error"), "Should not return error"
        
        # Son should be Tottenham forward
        assert "Spurs" in result, "Son should be from Spurs"
        assert ("FWD" in result or "MID" in result), "Son should be FWD or MID"

    def test_robertson_details(self):
        """Test get_player_details with Andrew Robertson (Liverpool defender)"""
        result = get_player_details("Robertson")
        print("Robertson details found")
        
        # Basic assertions
        assert isinstance(result, str), "Should return string result"
        assert not result.startswith("Error"), "Should not return error"
        
        # Robertson should be Liverpool defender
        assert "Liverpool" in result, "Robertson should be from Liverpool"
        assert "DEF" in result, "Robertson should be a defender"

    def test_gibbs_white_details(self):
        """Test get_player_details with Morgan Gibbs-White (hyphenated surname)"""
        result = get_player_details("Gibbs-White")
        print("Gibbs-White details found")
        
        # Basic assertions
        assert isinstance(result, str), "Should return string result"
        assert not result.startswith("Error"), "Should not return error"
        
        # Gibbs-White should be Nottingham Forest midfielder
        assert "Forest" in result, "Gibbs-White should be from Nottingham Forest"
        assert "MID" in result, "Gibbs-White should be a midfielder"

    def test_full_name_search_kane(self):
        """Test get_player_details with full name Harry Kane"""
        result = get_player_details("Harry Kane")
        print("Harry Kane full name search")
        
        # Basic assertions
        assert isinstance(result, str), "Should return string result"
        
        # If Harry Kane is found, should be consistent with just "Kane"
        kane_only_result = get_player_details("Kane")
        
        # Both should either succeed or fail consistently
        both_found = (not result.startswith("Error") and "not found" not in result.lower() and
                     not kane_only_result.startswith("Error") and "not found" not in kane_only_result.lower())
        both_not_found = (("not found" in result.lower() or result.startswith("❌")) and
                         ("not found" in kane_only_result.lower() or kane_only_result.startswith("❌")))
        
        assert both_found or both_not_found, "Full name and surname should be consistent"

    def test_brazilian_player_names(self):
        """Test get_player_details with Brazilian players (single names)"""
        # Test common Brazilian single names
        brazilian_names = ["Alisson", "Fabinho", "Ederson"]
        
        for name in brazilian_names:
            result = get_player_details(name)
            print(f"Testing Brazilian name: {name}")
            
            # Basic assertions
            assert isinstance(result, str), f"Should return string result for {name}"
            
            # If found, should have proper structure
            if not result.startswith("Error") and "not found" not in result.lower():
                assert "Team" in result, f"Should have team info for {name}"
                assert "Position" in result, f"Should have position info for {name}"

    def test_case_variations(self):
        """Test get_player_details with different case variations"""
        # Test the same player with different cases
        variations = [
            "salah",      # lowercase
            "SALAH",      # uppercase  
            "Salah",      # proper case
            "sAlAh"       # mixed case
        ]
        
        results = []
        for variation in variations:
            result = get_player_details(variation)
            results.append((variation, result))
        
        # All should return similar results (either all found or all not found)
        found_results = [(v, r) for v, r in results if not r.startswith("Error") and "not found" not in r.lower()]
        not_found_results = [(v, r) for v, r in results if "not found" in r.lower() or r.startswith("❌")]
        
        # Either all found or all not found (case shouldn't matter)
        assert len(found_results) == len(variations) or len(not_found_results) == len(variations), \
            "Case variations should be handled consistently"
        
        print(f"✅ Case variations test: {len(found_results)} found, {len(not_found_results)} not found")

    def test_partial_name_matching_edge_cases(self):
        """Test partial name matching with edge cases"""
        # Test names that might have multiple matches
        edge_cases = [
            ("Williams", "Should find a Williams"),
            ("Johnson", "Should find a Johnson"),
            ("Smith", "Should find a Smith"),
            ("Brown", "Should find a Brown")
        ]
        
        for name, description in edge_cases:
            result = get_player_details(name)
            print(f"Testing common surname: {name}")
            
            # Basic assertions
            assert isinstance(result, str), f"Should return string result for {name}"
            
            # If multiple players have the same surname, it should pick one consistently
            if not result.startswith("Error") and "not found" not in result.lower():
                assert "Team" in result, f"Should have team info for {name}"
                # Test that searching again gives the same result (consistency)
                result2 = get_player_details(name)
                assert result == result2, f"Should be consistent when searching {name} multiple times"

    def test_multiple_players_consistency(self):
        """Test consistency across different player searches"""
        players_to_test = [
            ("Rogers", "Morgan Rogers"),
            ("Salah", "Mohamed Salah"), 
            ("Haaland", "Erling Haaland"),
            ("Palmer", "Cole Palmer"),
            ("Son", "Son Heung-min")
        ]
        results = []
        
        for surname, full_description in players_to_test:
            result = get_player_details(surname)
            results.append((surname, result, full_description))
            
            # Each result should be consistent in format
            if not result.startswith("Error") and "not found" not in result.lower():
                assert "## Basic Info" in result, f"Should have Basic Info section for {surname}"
                assert "Team" in result, f"Should have team info for {surname}"
        
        # Count successful vs failed searches
        successful = sum(1 for _, result, _ in results 
                        if not result.startswith("Error") and "not found" not in result.lower())
        
        print(f"✅ Tested {len(players_to_test)} players, {successful} found successfully")


if __name__ == '__main__':
    # Run tests when executed directly
    pytest.main([__file__, '-v'])