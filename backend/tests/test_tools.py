import pytest
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools import get_easiest_fixtures, get_players_by_price_range, search_players


def test_get_easiest_fixtures_with_real_data():
    """Test get_easiest_fixtures using real FPL data"""
    
    # Change to the project root directory to access fpl_data
    original_dir = os.getcwd()
    # Go up from backend/tests to project root
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        # Test with default parameters (3 fixtures)
        result = get_easiest_fixtures()
        
        # Basic validation
        assert isinstance(result, str)
        assert len(result) > 0
        
        # Should not be an error message
        assert not result.startswith("Error calculating fixture difficulties:")
        
        # Should have multiple lines (one per team)
        lines = result.strip().split('\n')
        assert len(lines) > 0
        
        # Each line should have the expected format: "Team (X.X): Opponent1 (X), ..."
        for line in lines:
            assert '(' in line and ')' in line
            assert ':' in line
            
            # Extract team name and difficulty
            team_part, fixtures_part = line.split(':', 1)
            assert '(' in team_part  # Team name should have difficulty in parentheses
            
            # Validate fixtures format
            fixtures_part = fixtures_part.strip()
            if fixtures_part:  # Team has upcoming fixtures
                # Should contain opponent names and difficulty ratings
                assert '(' in fixtures_part and ')' in fixtures_part
        
        print(f"Test output with 3 fixtures:\n{result}\n")
        
    finally:
        os.chdir(original_dir)


def test_get_easiest_fixtures_custom_num_fixtures():
    """Test get_easiest_fixtures with custom number of fixtures"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        # Test with 5 fixtures
        result = get_easiest_fixtures(num_fixtures=5)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert not result.startswith("Error calculating fixture difficulties:")
        
        lines = result.strip().split('\n')
        assert len(lines) > 0
        
        print(f"Test output with 5 fixtures:\n{result}\n")
        
    finally:
        os.chdir(original_dir)


def test_get_easiest_fixtures_sorting():
    """Test that teams are sorted by difficulty (easiest first)"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        result = get_easiest_fixtures()
        
        if not result.startswith("Error"):
            lines = result.strip().split('\n')
            difficulties = []
            
            for line in lines:
                # Extract difficulty from "Team (X.X):" format
                team_part = line.split(':')[0]
                if '(' in team_part:
                    difficulty_str = team_part.split('(')[1].split(')')[0]
                    try:
                        difficulties.append(float(difficulty_str))
                    except ValueError:
                        pass  # Skip if difficulty can't be parsed
            
            # Verify they are in ascending order (easiest first)
            if len(difficulties) > 1:
                assert difficulties == sorted(difficulties), f"Difficulties not sorted: {difficulties}"
        
    finally:
        os.chdir(original_dir)


def test_get_easiest_fixtures_output_format():
    """Test the output format matches expected structure"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        result = get_easiest_fixtures(num_fixtures=2)
        
        if not result.startswith("Error"):
            lines = result.strip().split('\n')
            
            for line in lines:
                # Expected format: "Team Name (X.X): Opponent1 (X), Opponent2 (X)"
                assert ':' in line, f"Line missing colon: {line}"
                
                team_part, fixtures_part = line.split(':', 1)
                
                # Team part should have format "Team Name (X.X)"
                assert '(' in team_part and ')' in team_part, f"Team part missing parentheses: {team_part}"
                
                # Extract team name (everything before last opening parenthesis)
                team_name = team_part.rsplit('(', 1)[0].strip()
                assert len(team_name) > 0, f"Empty team name in: {team_part}"
                
                # Fixtures part should contain opponents with difficulties
                fixtures_part = fixtures_part.strip()
                if fixtures_part:  # Only check if team has fixtures
                    # Should contain at least one opponent with difficulty rating
                    assert '(' in fixtures_part and ')' in fixtures_part, f"Fixtures missing difficulty ratings: {fixtures_part}"
        
    finally:
        os.chdir(original_dir)


def test_get_players_by_price_range_default():
    """Test get_players_by_price_range with default parameters"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        result = get_players_by_price_range()
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert not result.startswith("Error getting players by price range:")
        
        lines = result.strip().split('\n')
        assert len(lines) > 2  # Header + empty line + at least one player
        
        # Check header format
        assert "Players in price range £4.0m - £15.0m" in lines[0]
        assert "found):" in lines[0]
        
        # Check that player lines contain expected format
        player_lines = [line for line in lines[2:] if line.strip()]  # Skip header and empty line
        for line in player_lines[:5]:  # Check first 5 players
            assert "(£" in line and "m)" in line  # Price format
            assert "(ID:" in line and line.endswith(")")  # ID format
            assert " - " in line  # Separator between name and team
        
    finally:
        os.chdir(original_dir)


def test_get_players_by_price_range_custom():
    """Test get_players_by_price_range with custom price range"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        # Test premium players range
        result = get_players_by_price_range(min_price=10.0, max_price=15.0)
        
        assert isinstance(result, str)
        assert not result.startswith("Error getting players by price range:")
        
        lines = result.strip().split('\n')
        assert "Players in price range £10.0m - £15.0m" in lines[0]
        
        # Check that all players are in the correct price range
        player_lines = [line for line in lines[2:] if line.strip()]
        for line in player_lines:
            # Extract price from format "(£X.Xm)"
            price_start = line.find("(£") + 2
            price_end = line.find("m)", price_start)
            if price_start > 1 and price_end > price_start:
                price_str = line[price_start:price_end]
                try:
                    price = float(price_str)
                    assert 10.0 <= price <= 15.0, f"Player price {price} outside range in: {line}"
                except ValueError:
                    pass  # Skip if price can't be parsed
        
    finally:
        os.chdir(original_dir)


def test_get_players_by_price_range_empty_range():
    """Test get_players_by_price_range with range that returns no players"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        # Test with impossibly high price range
        result = get_players_by_price_range(min_price=20.0, max_price=25.0)
        
        assert isinstance(result, str)
        assert "No players found in price range £20.0m - £25.0m" in result
        
    finally:
        os.chdir(original_dir)


def test_get_players_by_price_range_with_position():
    """Test get_players_by_price_range with position filtering"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        # Test defenders
        result = get_players_by_price_range(min_price=4.0, max_price=6.0, position='defender')
        
        assert isinstance(result, str)
        assert not result.startswith("Error getting players by price range:")
        assert "Defender in price range £4.0m - £6.0m" in result
        assert "found):" in result
        
        lines = result.strip().split('\n')
        player_lines = [line for line in lines[2:] if line.strip()]
        assert len(player_lines) > 0  # Should find defenders in this range
        
        # Test goalkeepers
        result_gk = get_players_by_price_range(min_price=4.0, max_price=5.0, position='goalkeeper')
        assert "Goalkeeper in price range £4.0m - £5.0m" in result_gk
        
        # Test midfielders
        result_mid = get_players_by_price_range(min_price=5.0, max_price=8.0, position='midfielder')
        assert "Midfielder in price range £5.0m - £8.0m" in result_mid
        
        # Test attackers
        result_att = get_players_by_price_range(min_price=8.0, max_price=12.0, position='attacker')
        assert "Attacker in price range £8.0m - £12.0m" in result_att
        
    finally:
        os.chdir(original_dir)


def test_get_players_by_price_range_invalid_position():
    """Test get_players_by_price_range with invalid position"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        # Test with invalid position - should default to all positions
        result = get_players_by_price_range(min_price=10.0, max_price=12.0, position='invalid_position')
        
        assert isinstance(result, str)
        assert not result.startswith("Error getting players by price range:")
        assert "All positions in price range £10.0m - £12.0m" in result
        
    finally:
        os.chdir(original_dir)


def test_get_players_by_price_range_no_position_found():
    """Test get_players_by_price_range when no players found for specific position"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        # Test goalkeepers in expensive range (unlikely to find any)
        result = get_players_by_price_range(min_price=15.0, max_price=20.0, position='goalkeeper')
        
        assert isinstance(result, str)
        assert "No goalkeepers found in price range £15.0m - £20.0m" in result
        
    finally:
        os.chdir(original_dir)


def test_search_players_most_expensive():
    """Test search_players for most expensive players"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        result = search_players('most expensive', 5)
        
        assert isinstance(result, str)
        assert not result.startswith("Error searching players:")
        assert "Most Expensive (Top 5):" in result
        
        lines = result.strip().split('\n')
        player_lines = [line for line in lines[2:] if line.strip()]
        assert len(player_lines) == 5
        
        # Check that all lines have the expected format
        for i, line in enumerate(player_lines, 1):
            assert line.startswith(f"{i}.")
            assert "(MID)" in line or "(FWD)" in line or "(DEF)" in line or "(GK)" in line
            assert "£" in line and "m" in line  # Price should be included
            assert "(ID:" in line and line.endswith(")")
        
    finally:
        os.chdir(original_dir)


def test_search_players_performance_metrics():
    """Test search_players for various performance metrics"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        # Test highest expected goals
        result_xg = search_players('highest expected goals', 3)
        assert "Highest Expected Goals (Top 3):" in result_xg
        assert not result_xg.startswith("Error searching players:")
        
        # Test most creative
        result_creative = search_players('most creative', 3)
        assert "Most Creative (Top 3):" in result_creative
        
        # Test highest total points
        result_points = search_players('highest total points', 3)
        assert "Highest Total Points (Top 3):" in result_points
        
        # Test most goals
        result_goals = search_players('most goals', 3)
        assert "Most Goals (Top 3):" in result_goals
        
    finally:
        os.chdir(original_dir)


def test_search_players_invalid_criteria():
    """Test search_players with invalid criteria"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        result = search_players('invalid criteria')
        
        assert isinstance(result, str)
        assert "Unknown criteria 'invalid criteria'" in result
        assert "Available criteria:" in result
        assert "most expensive" in result  # Should list available options
        
    finally:
        os.chdir(original_dir)


def test_search_players_custom_limit():
    """Test search_players with custom limit"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        result = search_players('most expensive', 15)
        
        assert isinstance(result, str)
        assert "Most Expensive (Top 15):" in result
        
        lines = result.strip().split('\n')
        player_lines = [line for line in lines[2:] if line.strip()]
        assert len(player_lines) == 15
        
        # Check that rankings are correct
        for i, line in enumerate(player_lines, 1):
            assert line.startswith(f"{i}.")
        
    finally:
        os.chdir(original_dir)


def test_search_players_case_insensitive():
    """Test search_players with case-insensitive criteria"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        # Test uppercase
        result1 = search_players('MOST EXPENSIVE', 3)
        assert "Most Expensive (Top 3):" in result1
        
        # Test mixed case
        result2 = search_players('Highest Expected Goals', 3)
        assert "Highest Expected Goals (Top 3):" in result2
        
        # Test partial match
        result3 = search_players('creative', 3)
        assert "Most Creative (Top 3):" in result3
        
    finally:
        os.chdir(original_dir)


def test_search_players_output_format():
    """Test search_players output format consistency"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        result = search_players('most expensive', 3)
        
        lines = result.strip().split('\n')
        
        # Check header format
        assert lines[0].endswith("(Top 3):")
        assert lines[1] == ""  # Empty line after header
        
        # Check player line format
        player_lines = lines[2:]
        for i, line in enumerate(player_lines, 1):
            parts = line.split(' - ')
            assert len(parts) >= 3  # Should have at least: name(pos), team, value(id)
            
            # Check ranking and name part
            name_part = parts[0]
            assert name_part.startswith(f"{i}.")
            assert "(" in name_part and ")" in name_part  # Position in parentheses
            
            # Check ID part
            id_part = parts[-1]
            assert id_part.startswith("(ID:") and id_part.endswith(")")
        
    finally:
        os.chdir(original_dir)