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