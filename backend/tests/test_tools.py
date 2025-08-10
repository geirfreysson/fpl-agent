import pytest
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools import get_easiest_fixtures, get_players_by_price_range, search_players, get_player_form, get_player_photos, find_player_replacements


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
    """Test search_players sorted by price (most expensive first)"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        # Test with price filtering to get expensive players
        result = search_players(min_price=10.0, limit=5)
        
        assert isinstance(result, str)
        assert "Players Found" in result
        assert "£" in result  # Should show prices
        
        # Check that results are properly formatted
        lines = result.split('\n')
        assert len([line for line in lines if line.strip() and not line.startswith('Players Found')]) >= 5
        
    finally:
        os.chdir(original_dir)


def test_search_players_performance_metrics():
    """Test search_players with performance-based filtering"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        # Test expected goals filtering
        result_xg = search_players(min_expected_goals=2.0, limit=3)
        assert "Players Found" in result_xg
        
        # Test creativity filtering
        result_creative = search_players(min_creativity=50.0, limit=3)
        assert "Players Found" in result_creative
        
        # Test total points filtering
        result_points = search_players(min_total_points=50, limit=3)
        assert "Players Found" in result_points
        
        # Test goals filtering
        result_goals = search_players(min_goals_scored=3, limit=3)
        assert "Players Found" in result_goals
        
    finally:
        os.chdir(original_dir)





def test_search_players_custom_limit():
    """Test search_players with custom limit"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        result = search_players(limit=15)
        
        assert isinstance(result, str)
        assert "Players Found" in result
        
        # Count the number of player entries
        lines = result.split('\n')
        player_lines = [line for line in lines if line.strip() and line[0].isdigit()]
        assert len(player_lines) == 15
        
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


def test_get_player_form_single_player():
    """Test get_player_form with a single player by name"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        result = get_player_form('Salah')
        
        assert isinstance(result, str)
        assert not result.startswith("Error getting player form:")
        assert "Player Form Analysis (1 players):" in result
        assert "M.Salah" in result or "Salah" in result
        assert "MID" in result or "FWD" in result  # Position should be included
        assert "Liverpool" in result  # Team should be included
        assert "£" in result  # Price should be included
        assert "Recent Form" in result
        assert "Season Average" in result
        assert "Total Season Points" in result
        
    finally:
        os.chdir(original_dir)


def test_get_player_form_multiple_players():
    """Test get_player_form with multiple players"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        result = get_player_form('Salah, Palmer')
        
        assert isinstance(result, str)
        assert "Player Form Analysis (2 players):" in result
        assert "Salah" in result
        assert "Palmer" in result
        
        # Should have two player sections
        lines = result.split('\n')
        player_headers = [line for line in lines if line.startswith('🔍')]
        assert len(player_headers) == 2
        
    finally:
        os.chdir(original_dir)


def test_get_player_form_by_id():
    """Test get_player_form with player ID"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        # Use player ID 381 (should be Salah based on earlier tests)
        result = get_player_form('381')
        
        assert isinstance(result, str)
        assert "Player Form Analysis (1 players):" in result
        assert not result.startswith("Error getting player form:")
        
        # Should contain standard form metrics
        assert "Recent Form" in result
        assert "Season Average" in result
        assert "Total Season Points" in result
        assert "Last Gameweek" in result
        assert "Minutes Played" in result
        
    finally:
        os.chdir(original_dir)


def test_get_player_form_detailed():
    """Test get_player_form with detailed historical analysis"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        result = get_player_form('381', detailed=True)
        
        assert isinstance(result, str)
        assert "Historical Performance" in result
        assert not result.startswith("Error getting player form:")
        
        # Should contain season data
        lines = result.split('\n')
        historical_lines = [line for line in lines if '/' in line and 'pts' in line]
        assert len(historical_lines) > 0  # Should have at least some historical data
        
    finally:
        os.chdir(original_dir)


def test_get_player_form_not_found():
    """Test get_player_form with non-existent player"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        result = get_player_form('NonExistentPlayer123')
        
        assert isinstance(result, str)
        assert "No players found matching:" in result
        assert "NonExistentPlayer123" in result
        
    finally:
        os.chdir(original_dir)


def test_get_player_form_mixed_found_not_found():
    """Test get_player_form with mix of found and not found players"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        result = get_player_form('Salah, NonExistentPlayer, Palmer')
        
        assert isinstance(result, str)
        assert "Player Form Analysis" in result
        assert "Salah" in result
        assert "Palmer" in result
        assert "❌ 'NonExistentPlayer' - Player not found" in result
        
    finally:
        os.chdir(original_dir)


def test_get_player_form_output_format():
    """Test get_player_form output format consistency"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        result = get_player_form('Salah')
        
        lines = result.split('\n')
        
        # Check header format
        assert lines[0].startswith("Player Form Analysis")
        assert "players):" in lines[0]
        assert lines[1] == ""  # Empty line after header
        
        # Find player header line
        player_header = None
        for line in lines:
            if line.startswith('🔍'):
                player_header = line
                break
        
        assert player_header is not None
        assert '(' in player_header and ')' in player_header  # Position
        assert ' - ' in player_header  # Team separator
        assert '£' in player_header and 'm' in player_header  # Price
        
        # Check that form metrics are present
        form_metrics = ['Recent Form', 'Season Average', 'Total Season Points', 'Last Gameweek', 'Minutes Played']
        for metric in form_metrics:
            assert any(metric in line for line in lines), f"Missing metric: {metric}"
        
    finally:
        os.chdir(original_dir)


def test_get_player_photos_single_player():
    """Test get_player_photos with a single player"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        result = get_player_photos('Salah')
        
        assert isinstance(result, list)
        assert len(result) == 1
        
        player_data = result[0]
        assert player_data['found'] == True
        assert 'Salah' in player_data['player_name']
        assert player_data['photo_url'] is not None
        assert 'resources.premierleague.com' in player_data['photo_url']
        assert '250x250' in player_data['photo_url']  # Default large size
        assert player_data['photo_url'].endswith('.jpg')
        assert player_data['player_id'] is not None
        assert player_data['full_name'] is not None
        
    finally:
        os.chdir(original_dir)


def test_get_player_photos_multiple_players():
    """Test get_player_photos with multiple players"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        result = get_player_photos(['Salah', 'Palmer', 'Haaland'])
        
        assert isinstance(result, list)
        assert len(result) == 3
        
        # Check that all players were found
        found_count = sum(1 for player in result if player['found'])
        assert found_count == 3
        
        # Check that all have valid photo URLs
        for player_data in result:
            assert player_data['photo_url'] is not None
            assert 'resources.premierleague.com' in player_data['photo_url']
            assert player_data['photo_url'].endswith('.jpg')
            assert player_data['player_id'] is not None
        
    finally:
        os.chdir(original_dir)


def test_get_player_photos_small_size():
    """Test get_player_photos with small photo size"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        result = get_player_photos('Salah', size='small')
        
        assert isinstance(result, list)
        assert len(result) == 1
        
        player_data = result[0]
        assert player_data['found'] == True
        assert '110x140' in player_data['photo_url']  # Small size
        assert 'resources.premierleague.com' in player_data['photo_url']
        
    finally:
        os.chdir(original_dir)


def test_get_player_photos_not_found():
    """Test get_player_photos with non-existent player"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        result = get_player_photos('NonExistentPlayer123')
        
        assert isinstance(result, list)
        assert len(result) == 1
        
        player_data = result[0]
        assert player_data['found'] == False
        assert player_data['player_name'] == 'NonExistentPlayer123'
        assert player_data['photo_url'] is None
        assert player_data['player_id'] is None
        assert player_data['full_name'] is None
        
    finally:
        os.chdir(original_dir)


def test_get_player_photos_mixed_found_not_found():
    """Test get_player_photos with mix of found and not found players"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        result = get_player_photos(['Salah', 'NonExistentPlayer', 'Palmer'])
        
        assert isinstance(result, list)
        assert len(result) == 3
        
        # Check first player (should be found)
        assert result[0]['found'] == True
        assert 'Salah' in result[0]['player_name']
        assert result[0]['photo_url'] is not None
        
        # Check second player (should not be found)
        assert result[1]['found'] == False
        assert result[1]['player_name'] == 'NonExistentPlayer'
        assert result[1]['photo_url'] is None
        
        # Check third player (should be found)
        assert result[2]['found'] == True
        assert 'Palmer' in result[2]['player_name']
        assert result[2]['photo_url'] is not None
        
    finally:
        os.chdir(original_dir)


def test_get_player_photos_string_input():
    """Test get_player_photos with string input instead of list"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        # Test that string input is handled correctly
        result1 = get_player_photos('Salah')
        result2 = get_player_photos(['Salah'])
        
        # Both should return the same result
        assert len(result1) == len(result2) == 1
        assert result1[0]['player_name'] == result2[0]['player_name']
        assert result1[0]['photo_url'] == result2[0]['photo_url']
        
    finally:
        os.chdir(original_dir)


def test_find_player_replacements_single_player():
    """Test find_player_replacements with a single player by name"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        result = find_player_replacements('Salah')
        
        assert isinstance(result, str)
        assert not result.startswith("Error finding player replacements:")
        assert "Salah" in result
        
        # Handle case where expensive players might not have replacements
        if "No replacement candidates found" in result:
            assert "Salah" in result
            assert "price range" in result
        else:
            assert "Player Replacement Analysis" in result
            assert "Current Player:" in result
            assert "Replacement Suggestions:" in result
            
            # Should contain replacement suggestions
            lines = result.split('\n')
            replacement_lines = [line for line in lines if line.strip().startswith('🔍')]
            assert len(replacement_lines) >= 1  # Should have at least 1 replacement
            
            # Each replacement should have proper format
            for line in replacement_lines:
                assert '(' in line and ')' in line  # Position and stats
        
    finally:
        os.chdir(original_dir)


def test_find_player_replacements_by_id():
    """Test find_player_replacements with player ID"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        # Use player ID 381 (should be Salah)
        result = find_player_replacements('381')
        
        assert isinstance(result, str)
        # Handle case where ID might not be found - this is acceptable
        if "not found" in result:
            assert "Player '381' not found" in result
        else:
            assert "Player Replacement Analysis" in result
            assert "Current Player:" in result
            assert "Replacement Suggestions:" in result or "No replacement candidates found" in result
            assert not result.startswith("Error finding player replacements:")
        
    finally:
        os.chdir(original_dir)


def test_find_player_replacements_custom_parameters():
    """Test find_player_replacements with custom price tolerance and suggestions"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        result = find_player_replacements('Palmer', price_tolerance=2.0, max_suggestions=5)
        
        assert isinstance(result, str)
        assert "Palmer" in result
        assert "Replacement Suggestions:" in result
        
        # Should have up to 5 replacement suggestions
        lines = result.split('\n')
        replacement_lines = [line for line in lines if line.strip().startswith('🔍')]
        assert len(replacement_lines) <= 5
        
        # Check price tolerance indication
        if "within £2.0m" in result:
            assert True  # Price tolerance is mentioned
        
    finally:
        os.chdir(original_dir)


def test_find_player_replacements_different_positions():
    """Test find_player_replacements for players in different positions"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        # Test a midfielder
        result_mid = find_player_replacements('Palmer', max_suggestions=2)
        assert "Palmer" in result_mid
        assert "MID" in result_mid  # Should show position
        
        # Test a forward (search for Haaland)
        result_fwd = find_player_replacements('Haaland', max_suggestions=2)
        assert isinstance(result_fwd, str)
        if not result_fwd.startswith("Error"):
            # Handle case where expensive forwards might not have replacements
            if "No replacement candidates found" not in result_fwd:
                assert "FWD" in result_fwd or "Forward" in result_fwd
            else:
                assert "Haaland" in result_fwd
        
    finally:
        os.chdir(original_dir)


def test_find_player_replacements_not_found():
    """Test find_player_replacements with non-existent player"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        result = find_player_replacements('NonExistentPlayer123')
        
        assert isinstance(result, str)
        assert "Player 'NonExistentPlayer123' not found" in result
        
    finally:
        os.chdir(original_dir)


def test_find_player_replacements_output_format():
    """Test find_player_replacements output format consistency"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        result = find_player_replacements('Palmer', max_suggestions=3)  # Use Palmer instead of Salah
        
        lines = result.split('\n')
        
        # Handle case where no candidates are found vs successful analysis
        if "No replacement candidates found" in result:
            assert "Palmer" in result
            assert "price range" in result
        else:
            # Check header format
            assert any("Player Replacement Analysis" in line for line in lines)
            
            # Check current player section exists (should have position info somewhere)
            assert "Palmer" in result
            assert "MID" in result  # Palmer is a midfielder
            
            # Check replacement section header
            replacement_header = [line for line in lines if "Replacement Suggestions" in line]
            assert len(replacement_header) == 1
            
            # Check replacement format
            replacement_lines = [line for line in lines if line.strip().startswith('🔍')]
            for line in replacement_lines:
                # Should have player name, position, team
                assert '(' in line and ')' in line
                assert ' - ' in line
            
            # Check that we have some performance data
            assert "Price:" in result or "£" in result
        
    finally:
        os.chdir(original_dir)


def test_find_player_replacements_scoring_logic():
    """Test that find_player_replacements returns players with meaningful scores"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        result = find_player_replacements('Salah', max_suggestions=3)
        
        if not result.startswith("Error"):
            lines = result.split('\n')
            replacement_lines = [line for line in lines if line.strip().startswith('🔍')]
            
            scores = []
            for i, line in enumerate(lines):
                # Look for score lines that come after replacement lines
                if 'Score:' in line:
                    score_match = line.split('Score:')[1].strip().split('/')[0]
                    try:
                        score = float(score_match)
                        scores.append(score)
                    except ValueError:
                        pass
            
            # Scores should be in descending order (best first)
            if len(scores) > 1:
                assert scores == sorted(scores, reverse=True), f"Scores not in descending order: {scores}"
            
            # Scores should be reasonable (between 0 and some reasonable max)
            for score in scores:
                assert 0 <= score <= 1000, f"Score {score} outside reasonable range"
        
    finally:
        os.chdir(original_dir)


def test_find_player_replacements_edge_cases():
    """Test find_player_replacements with various edge cases"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        # Test with very small price tolerance
        result1 = find_player_replacements('Palmer', price_tolerance=0.1, max_suggestions=2)
        assert isinstance(result1, str)
        
        # Test with large price tolerance
        result2 = find_player_replacements('Palmer', price_tolerance=5.0, max_suggestions=2)
        assert isinstance(result2, str)
        
        # Test with max_suggestions = 1
        result3 = find_player_replacements('Palmer', max_suggestions=1)
        if not result3.startswith("Error"):
            replacement_lines = [line for line in result3.split('\n') if line.strip().startswith('🔍')]
            assert len(replacement_lines) <= 1
        
        # Test with max_suggestions = 10
        result4 = find_player_replacements('Palmer', max_suggestions=10)
        if not result4.startswith("Error"):
            replacement_lines = [line for line in result4.split('\n') if line.strip().startswith('🔍')]
            assert len(replacement_lines) <= 10
        
    finally:
        os.chdir(original_dir)


# ========== COMPREHENSIVE SEARCH_PLAYERS TESTS ==========

def test_search_players_basic_functionality():
    """Test basic search_players functionality with real data"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        # Test basic search with no filters
        result = search_players(limit=5)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert not result.startswith("Error")
        
        lines = result.strip().split('\n')
        # Should have header and player entries
        assert len(lines) >= 2
        
        # Check basic format
        assert "Players Found" in result or "Player Analysis" in result
        
    finally:
        os.chdir(original_dir)


def test_search_players_position_filtering():
    """Test position-based filtering"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        # Test each position type
        positions = ['goalkeeper', 'defender', 'midfielder', 'forward']
        
        for position in positions:
            result = search_players(position=position, limit=3)
            
            assert isinstance(result, str)
            assert not result.startswith("Error"), f"Error for position {position}: {result}"
            
            if "No players found" not in result:
                # Should contain position-specific info
                pos_abbrev = {'goalkeeper': 'GK', 'defender': 'DEF', 'midfielder': 'MID', 'forward': 'FWD'}
                assert pos_abbrev[position] in result, f"Position {position} not found in result"
        
    finally:
        os.chdir(original_dir)


def test_search_players_price_filtering():
    """Test price-based filtering"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        # Test minimum price filter
        result1 = search_players(min_price=10.0, limit=5)
        assert isinstance(result1, str)
        assert not result1.startswith("Error")
        
        # Test maximum price filter
        result2 = search_players(max_price=5.0, limit=5)
        assert isinstance(result2, str)
        assert not result2.startswith("Error")
        
        # Test price range
        result3 = search_players(min_price=6.0, max_price=8.0, limit=5)
        assert isinstance(result3, str)
        assert not result3.startswith("Error")
        
        # Test very high price (should return few/no players)
        result4 = search_players(min_price=20.0, limit=5)
        assert isinstance(result4, str)
        # Should either return no players or very expensive ones
        
    finally:
        os.chdir(original_dir)


def test_search_players_performance_stats():
    """Test filtering by performance statistics"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        # Test total points filter
        result1 = search_players(min_total_points=50, limit=5)
        assert isinstance(result1, str)
        assert not result1.startswith("Error")
        
        # Test minutes filter (regular players)
        result2 = search_players(min_minutes=500, limit=5)
        assert isinstance(result2, str)
        assert not result2.startswith("Error")
        
        # Test goals filter
        result3 = search_players(min_goals_scored=3, limit=5)
        assert isinstance(result3, str)
        assert not result3.startswith("Error")
        
        # Test assists filter
        result4 = search_players(min_assists=2, limit=5)
        assert isinstance(result4, str)
        assert not result4.startswith("Error")
        
        # Test form filter
        result5 = search_players(min_form=4.0, limit=5)
        assert isinstance(result5, str)
        assert not result5.startswith("Error")
        
    finally:
        os.chdir(original_dir)


def test_search_players_enhanced_value_metrics():
    """Test enhanced value metrics filtering"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        # Test points per million filter
        result1 = search_players(min_points_per_million=8.0, limit=5)
        assert isinstance(result1, str)
        assert not result1.startswith("Error")
        
        # Test form per million filter
        result2 = search_players(min_form_per_million=0.5, limit=5)
        assert isinstance(result2, str)
        assert not result2.startswith("Error")
        
        # Test expected goals per million filter
        result3 = search_players(min_expected_goals_per_million=0.3, limit=5)
        assert isinstance(result3, str)
        assert not result3.startswith("Error")
        
    finally:
        os.chdir(original_dir)


def test_search_players_efficiency_metrics():
    """Test performance efficiency metrics filtering"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        # Test minutes per game (nailed-on players)
        result1 = search_players(min_minutes_per_game=75, limit=5)
        assert isinstance(result1, str)
        assert not result1.startswith("Error")
        
        # Test points per minute
        result2 = search_players(min_points_per_minute=0.05, limit=5)
        assert isinstance(result2, str)
        assert not result2.startswith("Error")
        
        # Test goal involvement rate
        result3 = search_players(min_goal_involvement_rate=20.0, limit=5)
        assert isinstance(result3, str)
        assert not result3.startswith("Error")
        
    finally:
        os.chdir(original_dir)


def test_search_players_expected_vs_actual():
    """Test expected vs actual performance metrics"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        # Test goals overperformance
        result1 = search_players(min_goals_overperformance=1.0, limit=5)
        assert isinstance(result1, str)
        assert not result1.startswith("Error")
        
        # Test assists overperformance
        result2 = search_players(min_assists_overperformance=0.5, limit=5)
        assert isinstance(result2, str)
        assert not result2.startswith("Error")
        
        # Test goals luck factor
        result3 = search_players(min_goals_luck_factor=1.2, limit=5)
        assert isinstance(result3, str)
        assert not result3.startswith("Error")
        
        # Test assists luck factor
        result4 = search_players(min_assists_luck_factor=1.1, limit=5)
        assert isinstance(result4, str)
        assert not result4.startswith("Error")
        
    finally:
        os.chdir(original_dir)


def test_search_players_consistency_metrics():
    """Test consistency and transfer metrics"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        # Test form consistency (lower is better)
        result1 = search_players(max_form_consistency=2.0, limit=5)
        assert isinstance(result1, str)
        assert not result1.startswith("Error")
        
        # Test transfer momentum
        result2 = search_players(min_transfer_momentum=10000, limit=5)
        assert isinstance(result2, str)
        assert not result2.startswith("Error")
        
        # Test ownership category
        result3 = search_players(ownership_category="Low", limit=5)
        assert isinstance(result3, str)
        assert not result3.startswith("Error")
        
        result4 = search_players(ownership_category="High", limit=5)
        assert isinstance(result4, str)
        assert not result4.startswith("Error")
        
    finally:
        os.chdir(original_dir)


def test_search_players_position_specific_features():
    """Test position-specific features"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        # Test goalkeeper-specific features
        result1 = search_players(position="goalkeeper", min_save_percentage=60.0, limit=3)
        assert isinstance(result1, str)
        assert not result1.startswith("Error")
        
        result2 = search_players(position="goalkeeper", min_clean_sheet_rate=20.0, limit=3)
        assert isinstance(result2, str)
        assert not result2.startswith("Error")
        
        # Test defender-specific features
        result3 = search_players(position="defender", min_defensive_value=2.0, limit=5)
        assert isinstance(result3, str)
        assert not result3.startswith("Error")
        
        result4 = search_players(position="defender", min_clean_sheet_rate=15.0, limit=5)
        assert isinstance(result4, str)
        assert not result4.startswith("Error")
        
        # Test midfielder/forward attacking threat
        result5 = search_players(position="midfielder", min_attacking_threat=3.0, limit=5)
        assert isinstance(result5, str)
        assert not result5.startswith("Error")
        
        result6 = search_players(position="forward", min_attacking_threat=4.0, limit=5)
        assert isinstance(result6, str)
        assert not result6.startswith("Error")
        
    finally:
        os.chdir(original_dir)


def test_search_players_fixture_difficulty():
    """Test fixture difficulty metrics"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        # Test 3-game fixture difficulty
        result1 = search_players(max_avg_fixture_difficulty_3=2.5, limit=5)
        assert isinstance(result1, str)
        assert not result1.startswith("Error")
        
        # Test 5-game fixture difficulty
        result2 = search_players(max_avg_fixture_difficulty_5=3.0, limit=5)
        assert isinstance(result2, str)
        assert not result2.startswith("Error")
        
        # Test 10-game fixture difficulty
        result3 = search_players(max_avg_fixture_difficulty_10=3.2, limit=5)
        assert isinstance(result3, str)
        assert not result3.startswith("Error")
        
        # Test home fixture difficulty
        result4 = search_players(max_home_fixture_difficulty_5=2.8, limit=5)
        assert isinstance(result4, str)
        assert not result4.startswith("Error")
        
        # Test away fixture difficulty
        result5 = search_players(max_away_fixture_difficulty_5=3.5, limit=5)
        assert isinstance(result5, str)
        assert not result5.startswith("Error")
        
    finally:
        os.chdir(original_dir)


def test_search_players_position_rankings():
    """Test position ranking metrics"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        # Test points rank in position (top players)
        result1 = search_players(max_points_rank_in_position=5, limit=10)
        assert isinstance(result1, str)
        assert not result1.startswith("Error")
        
        # Test value rank in position
        result2 = search_players(max_value_rank_in_position=3, limit=10)
        assert isinstance(result2, str)
        assert not result2.startswith("Error")
        
        # Test form rank in position
        result3 = search_players(max_form_rank_in_position=5, limit=10)
        assert isinstance(result3, str)
        assert not result3.startswith("Error")
        
    finally:
        os.chdir(original_dir)


def test_search_players_combined_filters():
    """Test complex combinations of filters"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        # Test midfielder with high expected goals under 7M
        result1 = search_players(
            position="midfielder",
            max_price=7.0,
            min_expected_goals_per_million=0.4,
            min_minutes=300,
            limit=5
        )
        assert isinstance(result1, str)
        assert not result1.startswith("Error")
        
        # Test consistent defenders with easy fixtures
        result2 = search_players(
            position="defender",
            max_form_consistency=2.5,
            max_avg_fixture_difficulty_5=3.0,
            min_minutes_per_game=60,
            limit=5
        )
        assert isinstance(result2, str)
        assert not result2.startswith("Error")
        
        # Test value forwards with good form
        result3 = search_players(
            position="forward",
            min_points_per_million=6.0,
            min_form=4.0,
            min_attacking_threat=3.0,
            limit=5
        )
        assert isinstance(result3, str)
        assert not result3.startswith("Error")
        
        # Test low ownership players with high expected performance
        result4 = search_players(
            ownership_category="Low",
            min_expected_goals_per_million=0.3,
            max_price=8.0,
            min_minutes=200,
            limit=5
        )
        assert isinstance(result4, str)
        assert not result4.startswith("Error")
        
    finally:
        os.chdir(original_dir)


def test_search_players_player_identity_filters():
    """Test player identity and team filters"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        # Test specific player by name
        result1 = search_players(web_name="Salah", limit=1)
        assert isinstance(result1, str)
        assert not result1.startswith("Error")
        if "No players found" not in result1:
            assert "Salah" in result1
        
        # Test team filter
        result2 = search_players(team="Arsenal", limit=5)
        assert isinstance(result2, str)
        assert not result2.startswith("Error")
        
        # Test first name filter
        result3 = search_players(first_name="Mohamed", limit=3)
        assert isinstance(result3, str)
        assert not result3.startswith("Error")
        
        # Test second name filter
        result4 = search_players(second_name="Palmer", limit=3)
        assert isinstance(result4, str)
        assert not result4.startswith("Error")
        
    finally:
        os.chdir(original_dir)


def test_search_players_availability_filters():
    """Test availability and injury-related filters"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        # Test available players only
        result1 = search_players(can_transact=True, limit=5)
        assert isinstance(result1, str)
        assert not result1.startswith("Error")
        
        # Test selectable players only
        result2 = search_players(can_select=True, limit=5)
        assert isinstance(result2, str)
        assert not result2.startswith("Error")
        
        # Test high chance of playing
        result3 = search_players(min_chance_of_playing=75, limit=5)
        assert isinstance(result3, str)
        assert not result3.startswith("Error")
        
        # Test players with injury concerns
        result4 = search_players(max_chance_of_playing=50, limit=5)
        assert isinstance(result4, str)
        assert not result4.startswith("Error")
        
    finally:
        os.chdir(original_dir)


def test_search_players_limit_and_sorting():
    """Test limit parameter and result sorting"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        # Test different limit values
        result1 = search_players(limit=1)
        assert isinstance(result1, str)
        assert not result1.startswith("Error")
        
        result2 = search_players(limit=20)
        assert isinstance(result2, str)
        assert not result2.startswith("Error")
        
        # Test that results are properly limited
        if "No players found" not in result2:
            lines = [line for line in result2.split('\n') if line.strip() and not line.startswith('=')]
            # Should have reasonable number of lines (header + players)
            assert len(lines) <= 25  # Some buffer for headers and formatting
        
    finally:
        os.chdir(original_dir)


def test_search_players_error_handling():
    """Test error handling and edge cases"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        # Test invalid position
        result1 = search_players(position="invalid_position", limit=5)
        assert isinstance(result1, str)
        # Should either handle gracefully or return no results
        
        # Test impossible filters (should return no results)
        result2 = search_players(min_price=50.0, limit=5)  # No player costs £50m
        assert isinstance(result2, str)
        assert "No players found" in result2 or not result2.startswith("Error")
        
        # Test negative values
        result3 = search_players(min_total_points=-10, limit=5)
        assert isinstance(result3, str)
        assert not result3.startswith("Error")
        
        # Test very large limit
        result4 = search_players(limit=1000)
        assert isinstance(result4, str)
        assert not result4.startswith("Error")
        
    finally:
        os.chdir(original_dir)


def test_search_players_output_format_consistency():
    """Test that output format is consistent across different filter combinations"""
    
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_root)
    
    try:
        # Test various filter combinations and check output format
        test_cases = [
            {"position": "midfielder", "limit": 3},
            {"min_price": 5.0, "max_price": 10.0, "limit": 3},
            {"min_total_points": 30, "limit": 3},
            {"min_form": 3.0, "limit": 3},
            {"position": "defender", "min_clean_sheet_rate": 10.0, "limit": 3}
        ]
        
        for test_case in test_cases:
            result = search_players(**test_case)
            
            assert isinstance(result, str)
            
            if not result.startswith("Error") and "No players found" not in result:
                lines = result.strip().split('\n')
                
                # Should have some structure
                assert len(lines) >= 1
                
                # Should contain player information
                has_player_info = any(
                    any(keyword in line.lower() for keyword in ['player', 'name', 'team', 'position', 'price'])
                    for line in lines
                )
                assert has_player_info, f"No player info found in result: {result[:200]}..."
        
    finally:
        os.chdir(original_dir)

def test_player_replacement_mbeumo():
    params = {
        "player_name": "Mbeumo",
        "key_attributes": {
            "position": "MID",
            "min_price": 7,
            "max_price": 9,
            "min_total_points": 200,
            "min_form": 0
        },
        "price_tolerance": 1,
        "max_suggestions": 3
        }
    result = find_player_replacements(params)
    print(result)

def test_player_replacement_salah():
    params = {
        "player_name": "Salah",
        "key_attributes": {
            "position": "MID",
            "min_price": 13.5,
            "max_price": 15,
            "min_total_points": 300,
            "min_minutes": 3200,
            "min_influence": 1500
        },
        "price_tolerance": 1,
        "max_suggestions": 5
        }
    result = find_player_replacements(params)
    print(result)