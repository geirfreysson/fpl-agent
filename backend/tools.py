import pandas as pd
import json
import os
from smolagents import tool

@tool
def get_weather(location: str) -> str:
    """
    Get the current weather for a given location.

    ONLY use this tool if the user has explicitly asked for the weather or if the weather can help solve the user's question.
    
    Args:
        location: The location to get weather for.
    """
    return f"The weather in {location} is sunny with a temperature of 72°F (22°C). Perfect day to be outside!"

@tool
def get_easiest_fixtures(num_fixtures: int = 3) -> str:
    """
    Calculate which teams have the easiest fixtures for a given period.
    
    Args:
        num_fixtures: Number of upcoming fixtures to analyze (default: 3)
    
    Returns:
        String with each team's average difficulty and fixture details
    """
    try:
        # Get the project root directory (go up from backend to project root)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        
        # Construct absolute paths to data files
        fixtures_path = os.path.join(project_root, 'fpl_data', 'fpl_data', 'fixtures.parquet')
        teams_path = os.path.join(project_root, 'fpl_data', 'fpl_data', 'teams.json')
        
        # Load fixtures data with only needed columns
        fixtures_df = pd.read_parquet(
            fixtures_path,
            columns=['team_h', 'team_a', 'team_h_difficulty', 'team_a_difficulty', 'event', 'finished']
        )
        
        # Load teams data for names
        with open(teams_path, 'r') as f:
            teams_data = json.load(f)
        team_lookup = {team['id']: team['name'] for team in teams_data}
        
        # Filter to unfinished fixtures and sort by event (gameweek)
        upcoming_fixtures = fixtures_df[fixtures_df['finished'] == False].sort_values('event')
        
        # Calculate team difficulties
        team_difficulties = {}
        
        # Process each team
        for team_id in team_lookup.keys():
            team_fixtures = []
            
            # Get all fixtures for this team (home and away) with event numbers
            home_fixtures = upcoming_fixtures[upcoming_fixtures['team_h'] == team_id][['team_a', 'team_h_difficulty', 'event']].copy()
            home_fixtures['opponent'] = home_fixtures['team_a'].map(team_lookup)
            home_fixtures['difficulty'] = home_fixtures['team_h_difficulty']
            
            away_fixtures = upcoming_fixtures[upcoming_fixtures['team_a'] == team_id][['team_h', 'team_a_difficulty', 'event']].copy()
            away_fixtures['opponent'] = away_fixtures['team_h'].map(team_lookup)
            away_fixtures['difficulty'] = away_fixtures['team_a_difficulty']
            
            # Combine and sort by event (chronological order)
            all_fixtures = pd.concat([
                home_fixtures[['opponent', 'difficulty', 'event']],
                away_fixtures[['opponent', 'difficulty', 'event']]
            ]).sort_values('event').head(num_fixtures)
            
            # Convert to list of tuples
            for _, fixture in all_fixtures.iterrows():
                team_fixtures.append((fixture['opponent'], fixture['difficulty']))
            
            if team_fixtures:
                avg_difficulty = sum(f[1] for f in team_fixtures) / len(team_fixtures)
                team_difficulties[team_id] = {
                    'avg_difficulty': avg_difficulty,
                    'fixtures': team_fixtures,
                    'name': team_lookup[team_id]
                }
        
        # Sort teams by average difficulty (easiest first)
        sorted_teams = sorted(team_difficulties.items(), key=lambda x: x[1]['avg_difficulty'])
        
        # Format output
        result_lines = []
        for team_id, data in sorted_teams:
            fixture_details = ", ".join([f"{opp} ({diff})" for opp, diff in data['fixtures']])
            result_lines.append(f"{data['name']} ({data['avg_difficulty']:.1f}): {fixture_details}")
        
        return "\n".join(result_lines)
        
    except Exception as e:
        return f"Error calculating fixture difficulties: {str(e)}"

@tool
def get_players_by_price_range(min_price: float = 4.0, max_price: float = 15.0, position: str = None) -> str:
    """
    Get all players within a specified price range and optionally filter by position.
    
    Args:
        min_price: Minimum price in millions (e.g., 4.0 for £4.0m)
        max_price: Maximum price in millions (e.g., 15.0 for £15.0m)
        position: Player position - 'goalkeeper', 'defender', 'midfielder', 'attacker' (optional)
    
    Returns:
        String with player names, IDs, teams, and prices
    """
    try:
        # Get the project root directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        
        # Construct absolute paths to data files
        elements_path = os.path.join(project_root, 'fpl_data', 'fpl_data', 'elements.parquet')
        teams_path = os.path.join(project_root, 'fpl_data', 'fpl_data', 'teams.json')
        
        # Load player data with only needed columns
        players_df = pd.read_parquet(
            elements_path,
            columns=['id', 'web_name', 'first_name', 'second_name', 'now_cost', 'team', 'element_type']
        )
        
        # Load teams data for names
        with open(teams_path, 'r') as f:
            teams_data = json.load(f)
        team_lookup = {team['id']: team['name'] for team in teams_data}
        
        # Convert price range from millions to 0.1m units (FPL format)
        min_cost = int(min_price * 10)  # e.g., 4.0 -> 40
        max_cost = int(max_price * 10)  # e.g., 15.0 -> 150
        
        # Position mapping: user input -> element_type
        position_mapping = {
            'goalkeeper': 1,
            'defender': 2, 
            'midfielder': 3,
            'attacker': 4
        }
        
        # Filter players by price range
        price_filter = (players_df['now_cost'] >= min_cost) & (players_df['now_cost'] <= max_cost)
        
        # Add position filter if specified
        if position and position.lower() in position_mapping:
            element_type = position_mapping[position.lower()]
            position_filter = players_df['element_type'] == element_type
            filtered_players = players_df[price_filter & position_filter].copy()
            position_display = position.capitalize()
        else:
            filtered_players = players_df[price_filter].copy()
            position_display = "All positions"
        
        if filtered_players.empty:
            if position:
                return f"No {position.lower()}s found in price range £{min_price}m - £{max_price}m"
            else:
                return f"No players found in price range £{min_price}m - £{max_price}m"
        
        # Add team names
        filtered_players['team_name'] = filtered_players['team'].map(team_lookup)
        
        # Convert cost back to millions for display
        filtered_players['price_display'] = filtered_players['now_cost'] / 10
        
        # Sort by price (ascending)
        filtered_players = filtered_players.sort_values('now_cost')
        
        # Format results
        result_lines = []
        result_lines.append(f"{position_display} in price range £{min_price}m - £{max_price}m ({len(filtered_players)} found):")
        result_lines.append("")
        
        for _, player in filtered_players.iterrows():
            # Format: "Player Name (£X.Xm) - Team (ID: X)"
            line = f"{player['web_name']} (£{player['price_display']:.1f}m) - {player['team_name']} (ID: {player['id']})"
            result_lines.append(line)
        
        return "\n".join(result_lines)
        
    except Exception as e:
        return f"Error getting players by price range: {str(e)}"

@tool
def search_players(criteria: str, limit: int = 10) -> str:
    """
    Search for players based on various criteria like performance, cost, or stats.
    
    Args:
        criteria: Search criteria (e.g., "most expensive", "highest expected goals", "most creative", 
                 "best form", "highest total points", "most assists", "most goals", "best threat", 
                 "highest influence", "best ict index", "most saves", "most clean sheets")
        limit: Number of players to return (default: 10)
    
    Returns:
        String with top players matching the criteria
    """
    try:
        # Get the project root directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        
        # Construct absolute paths to data files
        elements_path = os.path.join(project_root, 'fpl_data', 'fpl_data', 'elements.parquet')
        teams_path = os.path.join(project_root, 'fpl_data', 'fpl_data', 'teams.json')
        
        # Define criteria mappings: search term -> (column, ascending/descending, display_name)
        criteria_mappings = {
            # Cost criteria
            'most expensive': ('now_cost', False, 'Most Expensive'),
            'cheapest': ('now_cost', True, 'Cheapest'),
            
            # Points criteria
            'highest total points': ('total_points', False, 'Highest Total Points'),
            'best form': ('form', False, 'Best Form'),
            'highest points per game': ('points_per_game', False, 'Highest Points Per Game'),
            
            # Advanced metrics
            'most creative': ('creativity', False, 'Most Creative'),
            'highest threat': ('threat', False, 'Highest Threat'),
            'highest influence': ('influence', False, 'Highest Influence'),
            'best ict index': ('ict_index', False, 'Best ICT Index'),
            'highest expected goals': ('expected_goals', False, 'Highest Expected Goals'),
            'highest expected assists': ('expected_assists', False, 'Highest Expected Assists'),
            'highest expected goal involvements': ('expected_goal_involvements', False, 'Highest Expected Goal Involvements'),
            
            # Basic stats
            'most goals': ('goals_scored', False, 'Most Goals'),
            'most assists': ('assists', False, 'Most Assists'),
            'most minutes': ('minutes', False, 'Most Minutes Played'),
            'most saves': ('saves', False, 'Most Saves'),
            'most clean sheets': ('clean_sheets', False, 'Most Clean Sheets'),
        }
        
        # Find matching criteria (case insensitive)
        criteria_lower = criteria.lower()
        matching_criteria = None
        
        for key, value in criteria_mappings.items():
            if key in criteria_lower or criteria_lower in key:
                matching_criteria = value
                break
        
        if not matching_criteria:
            available_criteria = ', '.join(f'"{k}"' for k in sorted(criteria_mappings.keys()))
            return f"Unknown criteria '{criteria}'. Available criteria: {available_criteria}"
        
        sort_column, ascending, display_name = matching_criteria
        
        # Base columns always needed
        base_columns = ['id', 'web_name', 'first_name', 'second_name', 'team', 'element_type', 'now_cost']
        
        # Add the specific column for sorting if not already included
        columns_to_load = base_columns.copy()
        if sort_column not in columns_to_load:
            columns_to_load.append(sort_column)
        
        # Load player data with only needed columns
        players_df = pd.read_parquet(elements_path, columns=columns_to_load)
        
        # Load teams data for names
        with open(teams_path, 'r') as f:
            teams_data = json.load(f)
        team_lookup = {team['id']: team['name'] for team in teams_data}
        
        # Add team names
        players_df['team_name'] = players_df['team'].map(team_lookup)
        
        # Add position names
        position_lookup = {1: 'GK', 2: 'DEF', 3: 'MID', 4: 'FWD'}
        players_df['position'] = players_df['element_type'].map(position_lookup)
        
        # Convert price to millions for display
        players_df['price_display'] = players_df['now_cost'] / 10
        
        # Handle string columns that need to be converted to numeric
        if sort_column in ['form', 'points_per_game', 'creativity', 'threat', 'influence', 
                          'ict_index', 'expected_goals', 'expected_assists', 'expected_goal_involvements']:
            # Convert to numeric, handling empty strings and invalid values
            players_df[sort_column] = pd.to_numeric(players_df[sort_column], errors='coerce')
        
        # Remove players with NaN values in the sort column
        players_df = players_df.dropna(subset=[sort_column])
        
        # Sort by criteria
        sorted_players = players_df.sort_values(sort_column, ascending=ascending).head(limit)
        
        if sorted_players.empty:
            return f"No players found for criteria '{criteria}'"
        
        # Format results
        result_lines = []
        result_lines.append(f"{display_name} (Top {len(sorted_players)}):")
        result_lines.append("")
        
        for rank, (_, player) in enumerate(sorted_players.iterrows(), 1):
            # Get the value for display
            value = player[sort_column]
            
            # Format value based on column type
            if sort_column == 'now_cost':
                value_display = f"£{player['price_display']:.1f}m"
            elif sort_column in ['form', 'points_per_game', 'creativity', 'threat', 'influence', 
                               'ict_index', 'expected_goals', 'expected_assists', 'expected_goal_involvements']:
                value_display = f"{value:.1f}" if pd.notna(value) else "N/A"
            else:
                value_display = f"{int(value)}" if pd.notna(value) else "N/A"
            
            # Format: "1. Player Name (Position) - Team - Value (ID: X)"
            line = f"{rank}. {player['web_name']} ({player['position']}) - {player['team_name']} - {value_display} (ID: {player['id']})"
            result_lines.append(line)
        
        return "\n".join(result_lines)
        
    except Exception as e:
        return f"Error searching players: {str(e)}"

@tool
def get_player_form(players: str, detailed: bool = False) -> str:
    """
    Get form analysis for one or more players based on recent performance.
    
    Args:
        players: Comma-separated player IDs or names (e.g., "381, Palmer, Haaland")
        detailed: Include historical season comparison (default: False)
    
    Returns:
        String with player form analysis including recent form and season performance
    """
    try:
        # Get the project root directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        
        # Construct absolute paths to data files
        elements_path = os.path.join(project_root, 'fpl_data', 'fpl_data', 'elements.parquet')
        teams_path = os.path.join(project_root, 'fpl_data', 'fpl_data', 'teams.json')
        history_path = os.path.join(project_root, 'fpl_data', 'fpl_data', 'player_history_past.parquet')
        current_history_path = os.path.join(project_root, 'fpl_data', 'fpl_data', 'player_history.parquet')
        
        # Load player data
        players_df = pd.read_parquet(
            elements_path,
            columns=['id', 'web_name', 'first_name', 'second_name', 'team', 'element_type', 
                    'now_cost', 'form', 'points_per_game', 'total_points', 'event_points', 'minutes']
        )
        
        # Load teams data
        with open(teams_path, 'r') as f:
            teams_data = json.load(f)
        team_lookup = {team['id']: team['name'] for team in teams_data}
        
        # Add team names and positions
        players_df['team_name'] = players_df['team'].map(team_lookup)
        position_lookup = {1: 'GK', 2: 'DEF', 3: 'MID', 4: 'FWD'}
        players_df['position'] = players_df['element_type'].map(position_lookup)
        
        # Parse input players (could be IDs or names)
        player_inputs = [p.strip() for p in players.split(',')]
        found_players = []
        
        for player_input in player_inputs:
            player_input = player_input.strip()
            if not player_input:
                continue
                
            # Try to find by ID first
            if player_input.isdigit():
                player_id = int(player_input)
                player_row = players_df[players_df['id'] == player_id]
            else:
                # Search by name (web_name, first_name, or second_name)
                player_row = players_df[
                    players_df['web_name'].str.contains(player_input, case=False, na=False) |
                    players_df['first_name'].str.contains(player_input, case=False, na=False) |
                    players_df['second_name'].str.contains(player_input, case=False, na=False)
                ]
            
            if not player_row.empty:
                # Take the first match if multiple found
                found_players.append(player_row.iloc[0])
            else:
                found_players.append(None)  # Player not found
        
        if not any(p is not None for p in found_players):
            return f"No players found matching: {players}"
        
        # Load historical data if detailed analysis requested
        history_df = None
        if detailed:
            history_df = pd.read_parquet(
                history_path,
                columns=['player_id', 'season_name', 'total_points', 'minutes']
            )
        
        # Format results
        result_lines = []
        result_lines.append(f"Player Form Analysis ({len([p for p in found_players if p is not None])} players):")
        result_lines.append("")
        
        for i, (player_input, player_data) in enumerate(zip(player_inputs, found_players)):
            if player_data is None:
                result_lines.append(f"❌ '{player_input}' - Player not found")
                continue
            
            # Convert string values to numeric
            form = pd.to_numeric(player_data['form'], errors='coerce')
            ppg = pd.to_numeric(player_data['points_per_game'], errors='coerce')
            total_points = player_data['total_points']
            event_points = player_data['event_points']
            minutes = player_data['minutes']
            price = player_data['now_cost'] / 10
            
            # Player header
            result_lines.append(f"🔍 {player_data['web_name']} ({player_data['position']}) - {player_data['team_name']} (£{price:.1f}m)")
            
            # Calculate 30-day form if current season data is available
            thirty_day_form = None
            try:
                if os.path.exists(current_history_path):
                    current_history_df = pd.read_parquet(current_history_path)
                    player_current_history = current_history_df[current_history_df['player_id'] == player_data['id']]
                    
                    if not player_current_history.empty:
                        # Sort by round (gameweek) to get most recent games
                        player_current_history = player_current_history.sort_values('round', ascending=False)
                        
                        # For 30-day form, we'll approximate by taking last few gameweeks
                        # Since gameweeks are roughly weekly, ~4 weeks = ~4 gameweeks
                        recent_games = player_current_history.head(4)  # Last 4 gameweeks as 30-day approximation
                        
                        if len(recent_games) > 0:
                            total_points = recent_games['total_points'].sum()
                            thirty_day_form = total_points / len(recent_games)
            except:
                pass  # Fall back to existing form calculation
            
            # Display form analysis
            if thirty_day_form is not None:
                if thirty_day_form >= 6:
                    form_emoji = "🔥"
                    form_desc = "Excellent"
                elif thirty_day_form >= 4:
                    form_emoji = "⭐"
                    form_desc = "Good"
                elif thirty_day_form >= 2:
                    form_emoji = "📈"
                    form_desc = "Average"
                else:
                    form_emoji = "📉"
                    form_desc = "Poor"
                
                result_lines.append(f"   30-Day Form: {form_emoji} {thirty_day_form:.1f} points/game ({form_desc})")
            elif pd.notna(form) and form > 0:
                # Fall back to 5-game form if available
                if form >= 6:
                    form_emoji = "🔥"
                    form_desc = "Excellent"
                elif form >= 4:
                    form_emoji = "⭐"
                    form_desc = "Good"
                elif form >= 2:
                    form_emoji = "📈"
                    form_desc = "Average"
                else:
                    form_emoji = "📉"
                    form_desc = "Poor"
                
                result_lines.append(f"   Recent Form (5 games): {form_emoji} {form:.1f} points/game ({form_desc})")
            else:
                result_lines.append(f"   Recent Form: ❓ No recent games or data unavailable")
            
            # Season performance
            if pd.notna(ppg) and ppg > 0:
                result_lines.append(f"   Season Average: 📊 {ppg:.1f} points/game")
            else:
                result_lines.append(f"   Season Average: 📊 {total_points} total points")
            
            result_lines.append(f"   Total Season Points: 🎯 {total_points} points")
            result_lines.append(f"   Last Gameweek: 🎲 {event_points} points")
            result_lines.append(f"   Minutes Played: ⏱️ {minutes} minutes")
            
            # Historical comparison if detailed
            if detailed and history_df is not None:
                player_history = history_df[history_df['player_id'] == player_data['id']]
                if not player_history.empty:
                    # Get last 3 seasons for context
                    recent_seasons = player_history.sort_values('season_name', ascending=False).head(3)
                    
                    result_lines.append(f"   📈 Historical Performance:")
                    for _, season in recent_seasons.iterrows():
                        season_ppg = season['total_points'] / 38 if season['total_points'] > 0 else 0  # Assume 38 gameweeks
                        result_lines.append(f"      {season['season_name']}: {season['total_points']} pts ({season_ppg:.1f} ppg)")
                else:
                    result_lines.append(f"   📈 Historical Performance: No previous season data")
            
            # Add separator between players (except for last player)
            if i < len(found_players) - 1:
                result_lines.append("")
        
        return "\n".join(result_lines)
        
    except Exception as e:
        return f"Error getting player form: {str(e)}"

def get_player_photos(player_names, size="large"):
    """
    Get photo URLs for a list of player names.
    
    Args:
        player_names: List of player names or single player name string
        size: Photo size - "large" (250x250) or "small" (110x140)
    
    Returns:
        List of dictionaries with player name and photo URL
    """
    try:
        # Get the project root directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        
        # Construct absolute path to data file
        elements_path = os.path.join(project_root, 'fpl_data', 'fpl_data', 'elements.parquet')
        
        # Load player data with needed columns
        players_df = pd.read_parquet(
            elements_path,
            columns=['id', 'web_name', 'first_name', 'second_name', 'code', 'photo']
        )
        
        # Handle single string input
        if isinstance(player_names, str):
            player_names = [player_names]
        
        # Set photo size URL pattern
        if size == "small":
            url_pattern = "https://resources.premierleague.com/premierleague/photos/players/110x140/p{}.jpg"
        else:  # default to large
            url_pattern = "https://resources.premierleague.com/premierleague/photos/players/250x250/p{}.jpg"
        
        results = []
        
        for player_name in player_names:
            player_name = player_name.strip()
            if not player_name:
                continue
            
            # Search for player by name (web_name, first_name, or second_name)
            player_row = players_df[
                players_df['web_name'].str.contains(player_name, case=False, na=False) |
                players_df['first_name'].str.contains(player_name, case=False, na=False) |
                players_df['second_name'].str.contains(player_name, case=False, na=False)
            ]
            
            if not player_row.empty:
                # Take the first match if multiple found
                player = player_row.iloc[0]
                
                # Extract code from photo filename (remove .jpg extension)
                photo_code = player['code']
                
                # Construct photo URL
                photo_url = url_pattern.format(photo_code)
                
                results.append({
                    'player_name': player['web_name'],
                    'full_name': f"{player['first_name']} {player['second_name']}",
                    'player_id': player['id'],
                    'photo_url': photo_url,
                    'found': True
                })
            else:
                # Player not found
                results.append({
                    'player_name': player_name,
                    'full_name': None,
                    'player_id': None,
                    'photo_url': None,
                    'found': False
                })
        
        return results
        
    except Exception as e:
        # Return error information for each requested player
        if isinstance(player_names, str):
            player_names = [player_names]
        
        return [
            {
                'player_name': name,
                'full_name': None,
                'player_id': None,
                'photo_url': None,
                'found': False,
                'error': str(e)
            }
            for name in player_names
        ]

@tool
def find_player_replacements(player_name: str, price_tolerance: float = 1.0, max_suggestions: int = 3) -> str:
    """
    Find replacement players for a given player based on position, price, and performance.
    
    Args:
        player_name: Name of the player to find replacements for
        price_tolerance: Maximum price difference in millions (default: 1.0)
        max_suggestions: Number of replacement suggestions to return (default: 3)
    
    Returns:
        String with player replacement analysis and suggestions
    """
    try:
        # Get the project root directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        
        # Construct absolute paths to data files
        elements_path = os.path.join(project_root, 'fpl_data', 'fpl_data', 'elements.parquet')
        teams_path = os.path.join(project_root, 'fpl_data', 'fpl_data', 'teams.json')
        
        # Load player data with all needed columns for comparison
        players_df = pd.read_parquet(
            elements_path,
            columns=['id', 'web_name', 'first_name', 'second_name', 'team', 'element_type', 
                    'now_cost', 'form', 'points_per_game', 'total_points', 'expected_goals',
                    'expected_assists', 'expected_goal_involvements', 'creativity', 'threat',
                    'influence', 'ict_index', 'minutes', 'goals_scored', 'assists']
        )
        
        # Load teams data
        with open(teams_path, 'r') as f:
            teams_data = json.load(f)
        team_lookup = {team['id']: team['name'] for team in teams_data}
        
        # Add team names and positions
        players_df['team_name'] = players_df['team'].map(team_lookup)
        position_lookup = {1: 'GK', 2: 'DEF', 3: 'MID', 4: 'FWD'}
        players_df['position'] = players_df['element_type'].map(position_lookup)
        players_df['price'] = players_df['now_cost'] / 10  # Convert to millions
        
        # Find the target player
        target_player = players_df[
            players_df['web_name'].str.contains(player_name, case=False, na=False) |
            players_df['first_name'].str.contains(player_name, case=False, na=False) |
            players_df['second_name'].str.contains(player_name, case=False, na=False)
        ]
        
        if target_player.empty:
            return f"Player '{player_name}' not found. Please check the spelling and try again."
        
        # Take the first match if multiple found
        target = target_player.iloc[0]
        target_position = target['element_type']
        target_price = target['price']
        
        # Filter potential replacements
        # Same position, similar price, exclude the target player
        candidates = players_df[
            (players_df['element_type'] == target_position) &
            (players_df['price'] >= target_price - price_tolerance) &
            (players_df['price'] <= target_price + price_tolerance) &
            (players_df['id'] != target['id'])  # Exclude the target player
        ].copy()
        
        if candidates.empty:
            return f"No replacement candidates found for {target['web_name']} in the £{target_price - price_tolerance:.1f}m - £{target_price + price_tolerance:.1f}m price range."
        
        # Convert string columns to numeric for comparison
        numeric_columns = ['form', 'points_per_game', 'expected_goals', 'expected_assists', 
                          'expected_goal_involvements', 'creativity', 'threat', 'influence', 'ict_index']
        
        for col in numeric_columns:
            candidates[col] = pd.to_numeric(candidates[col], errors='coerce')
            target[col] = pd.to_numeric(target[col], errors='coerce') if pd.isna(pd.to_numeric(target[col], errors='coerce')) == False else 0
        
        # Calculate replacement score for each candidate
        def calculate_replacement_score(row, target_stats):
            score = 0
            
            # Total points (30% weight)
            if row['total_points'] > target_stats['total_points']:
                score += 30
            elif row['total_points'] >= target_stats['total_points'] * 0.9:
                score += 20
            elif row['total_points'] >= target_stats['total_points'] * 0.8:
                score += 10
            
            # Form (25% weight)
            target_form = target_stats['form'] if pd.notna(target_stats['form']) else 0
            if pd.notna(row['form']) and row['form'] > target_form:
                score += 25
            elif pd.notna(row['form']) and row['form'] >= target_form * 0.9:
                score += 15
            elif pd.notna(row['form']) and row['form'] >= target_form * 0.8:
                score += 5
            
            # Points per game (20% weight)
            target_ppg = target_stats['points_per_game'] if pd.notna(target_stats['points_per_game']) else 0
            if pd.notna(row['points_per_game']) and row['points_per_game'] > target_ppg:
                score += 20
            elif pd.notna(row['points_per_game']) and row['points_per_game'] >= target_ppg * 0.9:
                score += 15
            elif pd.notna(row['points_per_game']) and row['points_per_game'] >= target_ppg * 0.8:
                score += 10
            
            # Expected goals/assists (15% weight) - for attacking positions
            if target_stats['element_type'] in [3, 4]:  # MID, FWD
                target_xgi = target_stats['expected_goal_involvements'] if pd.notna(target_stats['expected_goal_involvements']) else 0
                if pd.notna(row['expected_goal_involvements']) and row['expected_goal_involvements'] > target_xgi:
                    score += 15
                elif pd.notna(row['expected_goal_involvements']) and row['expected_goal_involvements'] >= target_xgi * 0.9:
                    score += 10
            
            # Value for money (10% weight)
            target_value = target_stats['total_points'] / target_stats['price'] if target_stats['price'] > 0 else 0
            candidate_value = row['total_points'] / row['price'] if row['price'] > 0 else 0
            if candidate_value > target_value:
                score += 10
            elif candidate_value >= target_value * 0.9:
                score += 5
            
            return score
        
        # Calculate scores for all candidates
        candidates['replacement_score'] = candidates.apply(
            lambda row: calculate_replacement_score(row, target), axis=1
        )
        
        # Sort by score and get top suggestions
        top_candidates = candidates.sort_values('replacement_score', ascending=False).head(max_suggestions)
        
        # Format results
        result_lines = []
        result_lines.append(f"🔄 Player Replacement Analysis for {target['web_name']}")
        result_lines.append(f"📍 Position: {target['position']} | 💰 Price: £{target['price']:.1f}m | 🏆 Points: {target['total_points']}")
        result_lines.append("")
        
        if top_candidates.empty:
            result_lines.append("❌ No suitable replacements found with the current criteria.")
        else:
            result_lines.append(f"🎯 Top {len(top_candidates)} Replacement Suggestions:")
            result_lines.append("")
            
            for i, (_, candidate) in enumerate(top_candidates.iterrows(), 1):
                # Replacement header
                price_diff = candidate['price'] - target['price']
                price_symbol = "📈" if price_diff > 0 else "📉" if price_diff < 0 else "➡️"
                
                result_lines.append(f"{i}. 🔍 {candidate['web_name']} ({candidate['position']}) - {candidate['team_name']}")
                result_lines.append(f"   💰 Price: £{candidate['price']:.1f}m {price_symbol} ({price_diff:+.1f}m vs target)")
                result_lines.append(f"   🎯 Score: {candidate['replacement_score']:.0f}/100")
                
                # Performance comparison
                points_vs_target = candidate['total_points'] - target['total_points']
                points_symbol = "📈" if points_vs_target > 0 else "📉" if points_vs_target < 0 else "➡️"
                result_lines.append(f"   🏆 Points: {candidate['total_points']} {points_symbol} ({points_vs_target:+d} vs target)")
                
                # Form comparison
                candidate_form = candidate['form'] if pd.notna(candidate['form']) else 0
                target_form = target['form'] if pd.notna(target['form']) else 0
                form_vs_target = candidate_form - target_form
                form_symbol = "📈" if form_vs_target > 0 else "📉" if form_vs_target < 0 else "➡️"
                result_lines.append(f"   📊 Form: {candidate_form:.1f} {form_symbol} ({form_vs_target:+.1f} vs target)")
                
                # PPG comparison
                candidate_ppg = candidate['points_per_game'] if pd.notna(candidate['points_per_game']) else 0
                target_ppg = target['points_per_game'] if pd.notna(target['points_per_game']) else 0
                ppg_vs_target = candidate_ppg - target_ppg
                ppg_symbol = "📈" if ppg_vs_target > 0 else "📉" if ppg_vs_target < 0 else "➡️"
                result_lines.append(f"   ⚡ PPG: {candidate_ppg:.1f} {ppg_symbol} ({ppg_vs_target:+.1f} vs target)")
                
                # Add separator between candidates (except for last)
                if i < len(top_candidates):
                    result_lines.append("")
        
        return "\n".join(result_lines)
        
    except Exception as e:
        return f"Error finding player replacements: {str(e)}"