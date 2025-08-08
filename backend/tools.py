import pandas as pd
import numpy as np
import json
import os
import logging
import traceback
from smolagents import tool

@tool
def help() -> str:
    """
    Display helpful tips and example questions for FPL analysis using the enhanced features.
    
    Returns:
        String with comprehensive guide on available features and example queries
    """
    help_text = """
🏆 **FPL AGENT HELP GUIDE** 🏆

With our enhanced data features, you can ask sophisticated FPL questions! Here are some examples:

📊 **VALUE & EFFICIENCY ANALYSIS**
• "Find midfielders under £7m with high points per million"
• "Show me the best value defenders with good form per million"
• "Which forwards have the highest goal involvement rate?"
• "Find players with high points per minute (rotation-proof picks)"

🎯 **EXPECTED vs ACTUAL PERFORMANCE**
• "Show me players who are overperforming their expected goals" 
• "Find midfielders with positive assists overperformance"
• "Which players have the highest luck factor? (unsustainable performers)"
• "Show me consistent performers with low overperformance variance"

📈 **FIXTURE DIFFICULTY ANALYSIS**
• "Find teams with the easiest fixtures over the next 5 games"
• "Show me players from teams with favorable home fixtures"
• "Which defenders have easy fixtures and good clean sheet rates?"
• "Compare fixture difficulty for the next 3 vs 10 gameweeks"

🔄 **TRANSFER & OWNERSHIP TRENDS**
• "Show me players with high transfer momentum (rising in popularity)"
• "Find template players (high ownership) who are underperforming"
• "Which low-ownership gems have good underlying stats?"
• "Show me players being transferred out despite good metrics"

🏅 **POSITION-SPECIFIC ANALYSIS**
• **Goalkeepers**: "Find keepers with high save percentage and easy fixtures"
• **Defenders**: "Show me defenders with high defensive value and attacking threat"
• **Midfielders**: "Find mids with high attacking threat but low ownership"
• **Forwards**: "Which forwards have the best goal conversion rates?"

🎖️ **RANKING & COMPARISON**
• "Show me the top 5 value picks in each position"
• "Compare players' rank within their position for points vs form"
• "Find players ranked highly for value but low for ownership"
• "Which players have improved their position ranking recently?"

💡 **ADVANCED COMBINATION QUERIES**
• "Find midfielders under £8m with easy fixtures, positive overperformance, and rising transfer momentum"
• "Show me defenders with top 10 defensive value, good fixture difficulty, and low ownership"
• "Which forwards have high attacking threat, favorable fixtures, but are being transferred out?"
• "Find consistent performers (high form consistency) with upcoming easy fixtures"

🔍 **SPECIFIC FEATURE QUERIES**
• **Form Consistency**: "Show me the most consistent point scorers"
• **Minutes per Game**: "Find nailed-on starters in each position"
• **Clean Sheet Rate**: "Which keepers/defenders have the best clean sheet records?"
• **Save Percentage**: "Find keepers with high save rates for bonus points"

💰 **BUDGET & STRATEGY PLANNING**
• "Find the best value picks for a £100m budget"
• "Show me premium players (£10m+) who justify their price"
• "Which budget options (under £5m) offer the best returns?"
• "Find players with rising prices but still good value"

📋 **EXAMPLE COMPLEX QUERIES**
• "I need a midfielder under £7m who has easy fixtures, is gaining transfers, and outperforming expectations"
• "Show me defenders with top defensive value, good clean sheet rates, and favorable upcoming fixtures"
• "Find forwards with high attacking threat but low ownership - potential differentials"
• "Which players have the best combination of form, fixtures, and value?"

💭 **PRO TIPS**
• Combine multiple metrics for better insights (e.g., value + fixtures + form)
• Look for players with good underlying stats but low ownership (differentials)
• Consider fixture difficulty over different time horizons (3, 5, 10 games)
• Use overperformance metrics to identify sustainable vs lucky players
• Check transfer momentum to spot emerging trends before they peak

🚀 **GET STARTED**
Try asking: "Find me 3 midfielders under £8m with good value, easy fixtures, and positive transfer momentum"

Happy FPL managing! 🎯
"""
    return help_text


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

def _get_required_columns(filters: dict, sort_by: list) -> list:
    """Dynamically determine which columns to load based on filters and sorting"""
    required = {'id', 'web_name', 'team', 'element_type', 'now_cost', 'total_points', 'first_name', 'second_name'}
    
    # Column mapping for common aliases
    column_mapping = {
        'price': 'now_cost',
        'cost': 'now_cost', 
        'ownership': 'selected_by_percent',
        'name': 'web_name'
    }
    
    # Add columns from filters
    for key in filters.keys():
        if key.startswith(('min_', 'max_')):
            column = key[4:]  # Remove prefix
            # Map column name if it's an alias
            mapped_column = column_mapping.get(column, column)
            required.add(mapped_column)
        else:
            # Map column name if it's an alias
            mapped_column = column_mapping.get(key, key)
            required.add(mapped_column)
    
    # Add sort columns with mapping
    for col in sort_by:
        mapped_column = column_mapping.get(col, col)
        required.add(mapped_column)
    
    return list(required)

def _apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """Apply all filters using a single compound boolean mask"""
    mask = pd.Series(True, index=df.index)
    
    for key, value in filters.items():
        if value is None:
            continue
            
        if key.startswith('min_'):
            column = key[4:]  # Remove 'min_' prefix
            if column in df.columns:
                df[column] = pd.to_numeric(df[column], errors='coerce')
                
                # Special handling for chance_of_playing_next_round
                if column == 'chance_of_playing_next_round':
                    # SIMPLIFIED: For now, just use minutes_per_appearance as availability proxy
                    # Since most chance_of_playing values are null, use minutes as the primary metric
                    if 'minutes_per_appearance' in df.columns:
                        df['minutes_per_appearance'] = pd.to_numeric(df['minutes_per_appearance'], errors='coerce')
                        
                        # Convert percentage to realistic minutes threshold
                        if value >= 75:
                            minutes_threshold = 40
                        elif value >= 50:
                            minutes_threshold = 30  
                        elif value >= 25:
                            minutes_threshold = 20
                        else:
                            minutes_threshold = 10
                        
                        # Simple condition: players with good minutes per appearance
                        mask &= (df['minutes_per_appearance'].fillna(0) >= minutes_threshold)
                    else:
                        # Fallback: skip this filter if no minutes data
                        pass
                else:
                    mask &= (df[column] >= value)
        elif key.startswith('max_'):  
            column = key[4:]  # Remove 'max_' prefix
            if column in df.columns:
                df[column] = pd.to_numeric(df[column], errors='coerce')
                mask &= (df[column] <= value)
        elif key == 'position':
            position_map = {
                'goalkeeper': 1, 'gk': 1,
                'defender': 2, 'def': 2, 'defence': 2,
                'midfielder': 3, 'mid': 3, 'midfield': 3,
                'forward': 4, 'fwd': 4, 'attack': 4, 'attacker': 4
            }
            position_id = position_map.get(value.lower())
            if position_id:
                mask &= (df['element_type'] == position_id)
        elif key in ['first_name', 'second_name', 'web_name', 'team', 'status']:
            if key == 'team':
                mask &= df['team_name'].str.contains(value, case=False, na=False)
            elif key in df.columns:
                mask &= df[key].str.contains(value, case=False, na=False)
        elif key == 'player_id':
            mask &= (df['id'] == value)
        elif key == 'ownership_category' and 'ownership_category' in df.columns:
            mask &= df['ownership_category'].str.contains(value, case=False, na=False)
        elif key == 'is_penalty_taker' and 'penalties_order' in df.columns:
            df['penalties_order'] = pd.to_numeric(df['penalties_order'], errors='coerce')
            if value:
                mask &= (df['penalties_order'] > 0)
            else:
                mask &= ((df['penalties_order'] == 0) | df['penalties_order'].isna())
        elif key == 'is_corner_taker' and 'corners_and_indirect_freekicks_order' in df.columns:
            df['corners_and_indirect_freekicks_order'] = pd.to_numeric(df['corners_and_indirect_freekicks_order'], errors='coerce')
            if value:
                mask &= (df['corners_and_indirect_freekicks_order'] > 0)
            else:
                mask &= ((df['corners_and_indirect_freekicks_order'] == 0) | df['corners_and_indirect_freekicks_order'].isna())
        elif key == 'is_freekick_taker' and 'direct_freekicks_order' in df.columns:
            df['direct_freekicks_order'] = pd.to_numeric(df['direct_freekicks_order'], errors='coerce')
            if value:
                mask &= (df['direct_freekicks_order'] > 0)
            else:
                mask &= ((df['direct_freekicks_order'] == 0) | df['direct_freekicks_order'].isna())
        elif key == 'budget_enabler_price':
            exact_cost = int(value * 10)
            mask &= (df['now_cost'] == exact_cost)
        elif key in df.columns:
            mask &= (df[key] == value)
    
    return df[mask]

def _sort_results(df: pd.DataFrame, sort_by: list, ascending: list) -> pd.DataFrame:
    """Use pandas' native multi-column sorting with fallback handling"""
    fallback_map = {
        'price': 'now_cost',
        'cost': 'now_cost', 
        'ownership': 'selected_by_percent',
        'name': 'web_name'
    }
    
    valid_sort_columns = []
    valid_ascending = []
    
    for i, col in enumerate(sort_by):
        if col in df.columns:
            valid_sort_columns.append(col)
            valid_ascending.append(ascending[i])
        elif col in fallback_map and fallback_map[col] in df.columns:
            valid_sort_columns.append(fallback_map[col])
            valid_ascending.append(ascending[i])
        elif 'total_points' in df.columns:  # Fallback to total_points
            valid_sort_columns.append('total_points')
            valid_ascending.append(ascending[i])
    
    if not valid_sort_columns:
        return df  # Return unsorted if no valid columns
    
    return df.sort_values(by=valid_sort_columns, ascending=valid_ascending, na_position='last')

def _add_computed_columns(df: pd.DataFrame, team_lookup: dict) -> pd.DataFrame:
    """Add computed columns like team names and position names"""
    df['team_name'] = df['team'].map(team_lookup)
    position_lookup = {1: 'GK', 2: 'DEF', 3: 'MID', 4: 'FWD'}
    df['position'] = df['element_type'].map(position_lookup)
    df['price_display'] = df['now_cost'] / 10
    return df

@tool
def search_players(
    limit: int = 10,
    sort_by: str = "total_points",
    ascending: bool = False,
    filters: dict = None
) -> str:
    """
    Comprehensive player search with extensive filtering and multi-column sorting capabilities.
    
    POSITION OPTIONS: GK, DEF, MID, FWD
    
    FILTERING: Use filters dict with min_/max_ prefixes for ranges:
    - BASIC: position, team, player_id, status
    - COST: min_price, max_price, budget_enabler_price (exact price)
    - PERFORMANCE: min_total_points, max_total_points, min_form, max_form, min_points_per_game, max_points_per_game
    - OWNERSHIP: min_selected_by_percent, max_selected_by_percent
    - PLAYING TIME: min_minutes, max_minutes, min_minutes_per_game, max_minutes_per_game
    - GOALS/ASSISTS: min_goals_scored, max_goals_scored, min_assists, max_assists, min_own_goals, max_own_goals
    - VALUE METRICS: min_points_per_million, max_points_per_million, min_form_per_million, max_form_per_million
    - ADVANCED: min_expected_goals, max_expected_goals, min_expected_assists, max_expected_assists, min_expected_goal_involvements, max_expected_goal_involvements, min_expected_goals_conceded, max_expected_goals_conceded
    - EFFICIENCY: min_points_per_minute, max_points_per_minute, min_goal_involvement_rate, max_goal_involvement_rate
    - OVERPERFORMANCE: min_goals_overperformance, max_goals_overperformance, min_assists_overperformance, max_assists_overperformance
    - LUCK FACTORS: min_goals_luck_factor, max_goals_luck_factor, min_assists_luck_factor, max_assists_luck_factor
    - FIXTURES: min_avg_fixture_difficulty_3, max_avg_fixture_difficulty_3, min_avg_fixture_difficulty_5, max_avg_fixture_difficulty_5, min_avg_fixture_difficulty_10, max_avg_fixture_difficulty_10
    - POSITION SPECIFIC: min_save_percentage, max_save_percentage, min_clean_sheet_rate, max_clean_sheet_rate, min_attacking_threat, max_attacking_threat, min_defensive_value, max_defensive_value
    - PER 90 STATS: min_goals_per_90, max_goals_per_90, min_assists_per_90, max_assists_per_90, min_goal_involvements_per_90, max_goal_involvements_per_90
    - RANKINGS: min_points_rank_in_position, max_points_rank_in_position, min_value_rank_in_position, max_value_rank_in_position, min_form_rank_in_position, max_form_rank_in_position
    - BOOLEAN FLAGS: is_penalty_taker, is_corner_taker, is_freekick_taker
    - CATEGORIES: ownership_category (Low/Medium/High/Template)
    - ICT INDEX: min_influence, max_influence, min_creativity, max_creativity, min_threat, max_threat, min_ict_index, max_ict_index
    - CARDS: min_yellow_cards, max_yellow_cards, min_red_cards, max_red_cards
    - GOALKEEPER: min_saves, max_saves, min_goals_conceded, max_goals_conceded, min_penalties_saved, max_penalties_saved
    - PENALTIES: min_penalties_missed, max_penalties_missed
    - AVAILABILITY: min_chance_of_playing_next_round, max_chance_of_playing_next_round, can_transact, can_select
    - CAPTAIN POTENTIAL: min_captain_potential, max_captain_potential
    
    SORTING: 
    - SINGLE COLUMN: sort_by="total_points" (default), "form", "points_per_million", "ownership", etc.
    - MULTI-COLUMN: sort_by="selected_by_percent,total_points" (comma-separated, first=primary sort)
    - For requests like "low ownership but high points", use: sort_by="selected_by_percent,total_points" with ascending=True for ownership, False for points
    - All column names from elements.parquet are valid sort options including enhanced features

    Args:
        limit: Number of players to return (default: 10)
        sort_by: Single column or comma-separated columns for multi-level sorting
        ascending: Sort direction - False for highest first, True for lowest first (applies to all columns)
        filters: Dictionary of filters using column names with min_/max_ prefixes or exact matches
    
    Returns:
        String with formatted player results including applied filters summary
        
    Examples:
        # Simple searches
        search_players()  # Top 10 by total points
        search_players(sort_by="points_per_million", limit=5)
        search_players(filters={"position": "MID", "max_price": 8.0, "min_form": 5.0})
        
        # Multi-column sorting for complex requests
        search_players(sort_by="selected_by_percent,total_points", ascending=True, limit=5)  # Low ownership, high points
        search_players(sort_by="form,points_per_million", filters={"position": "FWD"})  # Best form forwards, then by value
        
        # Advanced filtering with enhanced features
        search_players(filters={"position": "DEF", "is_penalty_taker": True, "max_avg_fixture_difficulty_5": 3.0})
        search_players(filters={"min_goals_per_90": 0.4, "max_minutes_per_game": 75, "position": "FWD"})  # Rotation forwards
        search_players(filters={"ownership_category": "Low", "min_expected_goals_per_million": 0.5, "max_price": 7.0})
    """
    try:
        # Get data paths
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        elements_path = os.path.join(project_root, 'fpl_data', 'fpl_data', 'elements.parquet')
        teams_path = os.path.join(project_root, 'fpl_data', 'fpl_data', 'teams.json')
        
        # Default empty filters
        if filters is None:
            filters = {}
        
        # Handle price conversion in filters (from millions to FPL format)
        price_filters = {}
        for key, value in filters.items():
            if key in ['min_price', 'max_price']:
                column = 'min_now_cost' if key == 'min_price' else 'max_now_cost'
                price_filters[column] = int(value * 10)
            elif key in ['min_ownership', 'max_ownership']:
                column = 'min_selected_by_percent' if key == 'min_ownership' else 'max_selected_by_percent'
                price_filters[column] = value
            elif key in ['min_chance_of_playing', 'max_chance_of_playing']:
                column = 'min_chance_of_playing_this_round' if key == 'min_chance_of_playing' else 'max_chance_of_playing_this_round'
                price_filters[column] = value
            else:
                price_filters[key] = value
        
        # Normalize sort parameters - handle comma-separated strings
        if ',' in sort_by:
            sort_by_list = [col.strip() for col in sort_by.split(',')]
        else:
            sort_by_list = [sort_by]
        # Create ascending list with same length as sort_by_list
        ascending_list = [ascending] * len(sort_by_list)
        
        # Load only required columns
        required_columns = _get_required_columns(price_filters, sort_by_list)
        df = pd.read_parquet(elements_path, columns=required_columns)
        
        # Load teams data
        with open(teams_path, 'r') as f:
            teams_data = json.load(f)
        team_lookup = {team['id']: team['name'] for team in teams_data}
        
        # Add computed columns
        df = _add_computed_columns(df, team_lookup)
        
        # Apply all filters at once using compound mask
        filtered_df = _apply_filters(df, price_filters)
        
        if filtered_df.empty:
            return "No players found matching the specified criteria."
        
        # Sort using pandas native multi-column support
        sorted_df = _sort_results(filtered_df, sort_by_list, ascending_list)
        
        # Get top results
        result_df = sorted_df.head(limit)
        
        # Generate summary of applied filters
        applied_filters = []
        for k, v in price_filters.items():
            if v is not None:
                if k.startswith('min_'):
                    applied_filters.append(f"{k[4:]} >= {v}")
                elif k.startswith('max_'):
                    applied_filters.append(f"{k[4:]} <= {v}")
                else:
                    applied_filters.append(f"{k} = {v}")
        
        filter_summary = f"Applied filters: {', '.join(applied_filters)}" if applied_filters else "No filters applied"
        
        # Format results
        result_lines = []
        sort_desc = f"sorted by {', '.join(sort_by_list)}"
        result_lines.append(f"Found {len(result_df)} players ({sort_desc}):")
        result_lines.append(filter_summary)
        result_lines.append("")
        
        # Add each player
        for idx, (_, player) in enumerate(result_df.iterrows(), 1):
            player_line = f"{idx}. {player['web_name']} (£{player['price_display']:.1f}m) - {player['team_name']} ({player['position']}) - ID: {player['id']}"
            
            # Add key stats
            stats = [f"Points: {player['total_points']}"]
            
            # Add contextual stats based on available columns
            for col, label in [('form', 'Form'), ('selected_by_percent', 'Own'), ('points_per_game', 'PPG')]:
                if col in player and pd.notna(player[col]):
                    suffix = '%' if col == 'selected_by_percent' else ''
                    stats.append(f"{label}: {player[col]}{suffix}")
            
            # Add primary sort metric if different from basic stats
            if sort_by_list and len(sort_by_list) > 0:
                primary_sort = sort_by_list[0]
                if primary_sort in player and primary_sort not in ['total_points', 'web_name', 'now_cost', 'form', 'selected_by_percent', 'points_per_game']:
                    if pd.notna(player[primary_sort]):
                        stats.append(f"{primary_sort}: {player[primary_sort]}")
            
            if stats:
                player_line += f" | {' | '.join(stats)}"
            
            result_lines.append(player_line)
        
        return "\n".join(result_lines)
        
    except Exception as e:
        error_msg = str(e)
        logging.error(f"Error in search_players: {error_msg}")
        
        # Provide more helpful error messages
        if "No match for FieldRef.Name" in error_msg:
            # Extract the column name from the error
            import re
            match = re.search(r"No match for FieldRef\.Name\((\w+)\)", error_msg)
            if match:
                invalid_column = match.group(1)
                suggestion_map = {
                    'price': 'Try using "now_cost" or just omit sort_by to use default sorting',
                    'cost': 'Try using "now_cost" or just omit sort_by to use default sorting',
                    'ownership': 'Try using "selected_by_percent"',
                    'name': 'Try using "web_name"'
                }
                suggestion = suggestion_map.get(invalid_column, f'Column "{invalid_column}" not found in data')
                return f"Error: Invalid column '{invalid_column}' for sorting. {suggestion}"
        
        return f"Error searching players: {error_msg}"


@tool
def get_player_fixtures(players: str, num_fixtures: int = 5) -> str:
    """
    Get fixture difficulty analysis for specific players by mapping them to their teams.

    IMPORTANT: If you need fixtures for many players, send a comma seperated list.

    IMPORTANT: If available, send the player's ID instead of their names.
    
    Args:
        players: Comma-separated list of player names or IDs
        num_fixtures: Number of upcoming fixtures to analyze (default: 5)
    
    Returns:
        String with each player's team, average fixture difficulty, and detailed fixture list
    """
    try:
        # Get the project root directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        
        # Construct absolute paths to data files
        elements_path = os.path.join(project_root, 'fpl_data', 'fpl_data', 'elements.parquet')
        fixtures_path = os.path.join(project_root, 'fpl_data', 'fpl_data', 'fixtures.parquet')
        teams_path = os.path.join(project_root, 'fpl_data', 'fpl_data', 'teams.json')
        
        # Load player data
        players_df = pd.read_parquet(
            elements_path,
            columns=['id', 'web_name', 'first_name', 'second_name', 'team', 'element_type']
        )
        
        # Load fixtures data
        fixtures_df = pd.read_parquet(
            fixtures_path,
            columns=['team_h', 'team_a', 'team_h_difficulty', 'team_a_difficulty', 'event', 'finished']
        )
        
        # Load teams data for names
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
                # Search by name (web_name, first_name, or second_name) with improved matching
                # First try exact substring match
                player_row = players_df[
                    players_df['web_name'].str.contains(player_input, case=False, na=False) |
                    players_df['first_name'].str.contains(player_input, case=False, na=False) |
                    players_df['second_name'].str.contains(player_input, case=False, na=False)
                ]
                
                # If no matches, try with normalized spacing (remove spaces and dots)
                if player_row.empty:
                    normalized_input = player_input.replace(' ', '').replace('.', '')
                    player_row = players_df[
                        players_df['web_name'].str.replace(' ', '').str.replace('.', '').str.contains(normalized_input, case=False, na=False) |
                        players_df['first_name'].str.replace(' ', '').str.replace('.', '').str.contains(normalized_input, case=False, na=False) |
                        players_df['second_name'].str.replace(' ', '').str.replace('.', '').str.contains(normalized_input, case=False, na=False)
                    ]
            
            if not player_row.empty:
                # Take the first match if multiple found
                found_players.append(player_row.iloc[0])
            else:
                found_players.append(None)  # Player not found
        
        if not any(p is not None for p in found_players):
            return f"No players found matching: {players}"
        
        # Filter to unfinished fixtures and sort by event (gameweek)
        upcoming_fixtures = fixtures_df[fixtures_df['finished'] == False].sort_values('event')
        
        # Format results
        result_lines = []
        result_lines.append(f"Player Fixture Analysis ({len([p for p in found_players if p is not None])} players, next {num_fixtures} fixtures):")
        result_lines.append("")
        
        for i, (player_input, player_data) in enumerate(zip(player_inputs, found_players)):
            if player_data is None:
                result_lines.append(f"'{player_input}' - Player not found")
                continue
            
            team_id = player_data['team']
            team_name = player_data['team_name']
            
            # Calculate fixture difficulty for this player's team using same algorithm as get_easiest_fixtures
            
            # Get all fixtures for this team (home and away) with event numbers
            home_fixtures = upcoming_fixtures[upcoming_fixtures['team_h'] == team_id][['team_a', 'team_h_difficulty', 'event']].copy()
            if not home_fixtures.empty:
                home_fixtures['opponent'] = home_fixtures['team_a'].map(team_lookup)
                home_fixtures['difficulty'] = home_fixtures['team_h_difficulty']
                home_fixtures['venue'] = 'H'  # Home
            
            away_fixtures = upcoming_fixtures[upcoming_fixtures['team_a'] == team_id][['team_h', 'team_a_difficulty', 'event']].copy()
            if not away_fixtures.empty:
                away_fixtures['opponent'] = away_fixtures['team_h'].map(team_lookup)
                away_fixtures['difficulty'] = away_fixtures['team_a_difficulty']
                away_fixtures['venue'] = 'A'  # Away
            
            # Combine and sort by event (chronological order)
            all_fixtures = []
            if not home_fixtures.empty:
                all_fixtures.append(home_fixtures[['opponent', 'difficulty', 'event', 'venue']])
            if not away_fixtures.empty:
                all_fixtures.append(away_fixtures[['opponent', 'difficulty', 'event', 'venue']])
            
            if all_fixtures:
                combined_fixtures = pd.concat(all_fixtures).sort_values('event').head(num_fixtures)
                
                # Convert to list of tuples with venue info
                fixture_list = []
                for _, fixture in combined_fixtures.iterrows():
                    fixture_list.append((
                        fixture['opponent'], 
                        fixture['difficulty'], 
                        fixture['venue']
                    ))
                
                if fixture_list:
                    avg_difficulty = sum(f[1] for f in fixture_list) / len(fixture_list)
                    
                    # Player header
                    result_lines.append(f"{player_data['web_name']} ({player_data['position']}) - {team_name}")
                    result_lines.append(f"  Average Fixture Difficulty: {avg_difficulty:.1f}")
                    result_lines.append(f"  Upcoming Fixtures:")
                    
                    for opponent, difficulty, venue in fixture_list:
                        venue_text = "(H)" if venue == 'H' else "(A)"
                        result_lines.append(f"    vs {opponent} {venue_text} - Difficulty: {difficulty}")
                else:
                    result_lines.append(f"{player_data['web_name']} ({player_data['position']}) - {team_name}")
                    result_lines.append(f"  No upcoming fixtures found")
            else:
                result_lines.append(f"{player_data['web_name']} ({player_data['position']}) - {team_name}")
                result_lines.append(f"  No upcoming fixtures found")
            
            # Add separator between players (except for last player)
            if i < len(found_players) - 1:
                result_lines.append("")
        
        # Clean the result for JSON safety
        final_result = "\n".join(result_lines)
        # Remove any problematic characters that could break JSON
        final_result = final_result.replace('"', "'").replace('\\', '/').replace('\r', '').replace('\x00', '')
        return final_result
        
    except Exception as e:
        error_msg = f"Error getting player fixtures: {str(e)}"
        # Clean error message for JSON safety
        return error_msg.replace('"', "'").replace('\\', '/').replace('\r', '').replace('\x00', '')

@tool
def get_player_form(players: str, detailed: bool = False) -> str:
    """
    Get form analysis for one or more players based on recent performance.

    IMPORTANT: If you need the form for many players, only call this tool once and 
    pass the player IDs or names as a comma-separated string.
    
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
                # Search by name (web_name, first_name, or second_name) with improved matching
                # First try exact substring match
                player_row = players_df[
                    players_df['web_name'].str.contains(player_input, case=False, na=False) |
                    players_df['first_name'].str.contains(player_input, case=False, na=False) |
                    players_df['second_name'].str.contains(player_input, case=False, na=False)
                ]
                
                # If no matches, try with normalized spacing (remove spaces and dots)
                if player_row.empty:
                    normalized_input = player_input.replace(' ', '').replace('.', '')
                    player_row = players_df[
                        players_df['web_name'].str.replace(' ', '').str.replace('.', '').str.contains(normalized_input, case=False, na=False) |
                        players_df['first_name'].str.replace(' ', '').str.replace('.', '').str.contains(normalized_input, case=False, na=False) |
                        players_df['second_name'].str.replace(' ', '').str.replace('.', '').str.contains(normalized_input, case=False, na=False)
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
            result_lines.append(f"{player_data['web_name']} ({player_data['position']}) - {player_data['team_name']} (£{price:.1f}m)")
            
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
                    form_desc = "Excellent"
                elif thirty_day_form >= 4:
                    form_desc = "Good"
                elif thirty_day_form >= 2:
                    form_desc = "Average"
                else:
                    form_desc = "Poor"
                
                result_lines.append(f"  30-Day Form: {thirty_day_form:.1f} points/game ({form_desc})")
            elif pd.notna(form) and form > 0:
                # Fall back to 5-game form if available
                if form >= 6:
                    form_desc = "Excellent"
                elif form >= 4:
                    form_desc = "Good"
                elif form >= 2:
                    form_desc = "Average"
                else:
                    form_desc = "Poor"
                
                result_lines.append(f"  Recent Form: {form:.1f} points/game ({form_desc})")
            else:
                result_lines.append(f"  Recent Form: No recent data available")
            
            # Season performance (concise)
            if pd.notna(ppg) and ppg > 0:
                result_lines.append(f"  Season: {ppg:.1f} ppg, {total_points} total pts, {event_points} last GW")
            else:
                result_lines.append(f"  Season: {total_points} total pts, {event_points} last GW")
            result_lines.append(f"  Minutes: {minutes}")
            
            # Historical comparison if detailed
            if detailed and history_df is not None:
                player_history = history_df[history_df['player_id'] == player_data['id']]
                if not player_history.empty:
                    # Get last 2 seasons for context (reduced from 3)
                    recent_seasons = player_history.sort_values('season_name', ascending=False).head(2)
                    
                    result_lines.append(f"  Historical:")
                    for _, season in recent_seasons.iterrows():
                        season_ppg = season['total_points'] / 38 if season['total_points'] > 0 else 0
                        result_lines.append(f"    {season['season_name']}: {season['total_points']} pts ({season_ppg:.1f} ppg)")
                else:
                    result_lines.append(f"  Historical: No previous data")
            
            # Add separator between players (except for last player)
            if i < len(found_players) - 1:
                result_lines.append("")
        
        # Clean the result for JSON safety
        final_result = "\n".join(result_lines)
        # Remove any problematic characters that could break JSON
        final_result = final_result.replace('"', "'").replace('\\', '/').replace('\r', '').replace('\x00', '')
        return final_result
        
    except Exception as e:
        error_msg = f"Error getting player form: {str(e)}"
        # Clean error message for JSON safety
        return error_msg.replace('"', "'").replace('\\', '/').replace('\r', '').replace('\x00', '')

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
def get_player_details(player_identifier: str) -> str:
    """
    Get comprehensive details about a specific player including all statistics, rankings, and tier information.
    This tool provides a complete player profile with performance metrics, value analysis, and position rankings.
    
    Args:
        player_identifier: Player name or ID to get details for
    
    Returns:
        String with comprehensive player analysis including tier classification and detailed rankings
    """
    try:
        # Get the project root directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        
        # Construct absolute paths to data files
        elements_path = os.path.join(project_root, 'fpl_data', 'fpl_data', 'elements.parquet')
        teams_path = os.path.join(project_root, 'fpl_data', 'fpl_data', 'teams.json')
        
        # Load data
        elements_df = pd.read_parquet(elements_path)
        with open(teams_path, 'r') as f:
            teams_data = json.load(f)
        
        # Create teams lookup
        teams_dict = {team['id']: team for team in teams_data}
        
        # Parse player input (could be ID or name) - same logic as get_player_fixtures
        player_input = player_identifier.strip()
        
        # Try to find by ID first
        if player_input.isdigit():
            player_id = int(player_input)
            player_row = elements_df[elements_df['id'] == player_id]
        else:
            # Search by name (web_name, first_name, or second_name) with improved matching
            # First try exact substring match
            player_row = elements_df[
                elements_df['web_name'].str.contains(player_input, case=False, na=False) |
                elements_df['first_name'].str.contains(player_input, case=False, na=False) |
                elements_df['second_name'].str.contains(player_input, case=False, na=False)
            ]
            
            # If no matches, try with normalized spacing (remove spaces and dots)
            if player_row.empty:
                normalized_input = player_input.replace(' ', '').replace('.', '')
                player_row = elements_df[
                    elements_df['web_name'].str.replace(' ', '').str.replace('.', '').str.contains(normalized_input, case=False, na=False) |
                    elements_df['first_name'].str.replace(' ', '').str.replace('.', '').str.contains(normalized_input, case=False, na=False) |
                    elements_df['second_name'].str.replace(' ', '').str.replace('.', '').str.contains(normalized_input, case=False, na=False)
                ]
        
        if player_row.empty:
            return f"❌ Player '{player_identifier}' not found. Please check the spelling or try a different name/ID."
        
        # Take the first match if multiple found
        player = player_row.iloc[0]
        
        # Get team info
        team_info = teams_dict.get(player['team'], {})
        team_name = team_info.get('name', 'Unknown')
        
        # Position mapping
        position_map = {1: 'GK', 2: 'DEF', 3: 'MID', 4: 'FWD'}
        position = position_map.get(player['element_type'], 'Unknown')
        
        # Calculate tier classification based on multiple metrics
        position_players = elements_df[elements_df['element_type'] == player['element_type']]
        
        # Tier calculation based on multiple factors
        total_points_percentile = (position_players['total_points'] < player['total_points']).mean() * 100
        value_percentile = (position_players['points_per_million'] < player['points_per_million']).mean() * 100
        form_percentile = (position_players['form'] < player['form']).mean() * 100
        
        # Combined tier score (weighted average)
        tier_score = (total_points_percentile * 0.4 + value_percentile * 0.3 + form_percentile * 0.3)
        
        if tier_score >= 90:
            tier = "🏆 ELITE (Top 10%)"
        elif tier_score >= 75:
            tier = "⭐ PREMIUM (Top 25%)"
        elif tier_score >= 50:
            tier = "📈 SOLID (Top 50%)"
        elif tier_score >= 25:
            tier = "📊 DECENT (Top 75%)"
        else:
            tier = "⚠️ BUDGET/BENCH (Bottom 25%)"
        
        # Get rankings within position
        position_rankings = {}
        ranking_columns = {
            'total_points': 'Total Points',
            'points_per_million': 'Value (PPM)',
            'form': 'Form (5 games)',
            'selected_by_percent': 'Ownership %',
            'minutes': 'Minutes Played',
            'goals_scored': 'Goals',
            'assists': 'Assists',
            'clean_sheets': 'Clean Sheets',
            'goals_conceded': 'Goals Conceded',
            'own_goals': 'Own Goals',
            'penalties_saved': 'Penalties Saved',
            'penalties_missed': 'Penalties Missed',
            'yellow_cards': 'Yellow Cards',
            'red_cards': 'Red Cards',
            'saves': 'Saves',
            'bonus': 'Bonus Points',
            'bps': 'BPS',
            'influence': 'Influence',
            'creativity': 'Creativity',
            'threat': 'Threat',
            'ict_index': 'ICT Index'
        }
        
        for col, display_name in ranking_columns.items():
            if col in position_players.columns and pd.notna(player[col]):
                rank = (position_players[col] > player[col]).sum() + 1
                total_in_position = len(position_players)
                position_rankings[display_name] = f"{rank}/{total_in_position}"
        
        section_dfs = extract_player_sections(
            player=player,
            team_name=team_name,
            position=position,
            tier=tier,
            position_rankings=position_rankings
        )
        result = ""
        for section, df in section_dfs.items():
            result += f"## {section}\n"
            result += df.to_markdown(index=False)
            result += "\n"
        
        return result
        
    except Exception as e:
        error_msg = f"Error getting player details for '{player_identifier}': {str(e)}"
        logging.error(f"Error in get_player_details: {e}")
        logging.error(traceback.format_exc())
        return error_msg.replace('"', "'").replace('\\', '/').replace('\r', '').replace('\x00', '')

def extract_player_sections(player: dict, team_name: str, position: str, tier: str, position_rankings: dict) -> dict:
    """
    Given a player record and derived metadata, return a dictionary of DataFrames per section,
    with columns: Metric, Value, Rank.
    """
    def row(metric, value, rank=None):
        return {"Metric": metric, "Value": value, "Rank": rank}

    sections = {}

    # Basic Info
    sections["Basic Info"] = pd.DataFrame([
        row("Team", team_name),
        row("Position", position),
        row("Price", f"£{player['now_cost'] / 10:.1f}m"),
        row("Tier", tier),
        row("Ownership", f"{player['selected_by_percent']:.1f}%")
    ])

    # Season Statistics
    sections["Season Statistics"] = pd.DataFrame([
        row("Total Points", player["total_points"], position_rankings.get("Total Points")),
        row("Points per Game", f"{player['points_per_game']:.1f}"),
        row("Minutes Played", player["minutes"], position_rankings.get("Minutes Played")),
        row("Bonus Points", player["bonus"], position_rankings.get("Bonus Points"))
    ])

    # Value Analysis
    sections["Value Analysis"] = pd.DataFrame([
        row("Points per Million", f"{player['points_per_million']:.1f}", position_rankings.get("Value (PPM)")),
        row("Form per Million", f"{player.get('form_per_million', 0):.1f}"),
        row("Form (5 games)", f"{player['form']:.1f}", position_rankings.get("Form (5 games)"))
    ])

    # Performance Metrics
    metrics = []
    if position == "GK":
        metrics = [
            row("Saves", player["saves"], position_rankings.get("Saves")),
            row("Clean Sheets", player["clean_sheets"], position_rankings.get("Clean Sheets")),
            row("Goals Conceded", player["goals_conceded"], position_rankings.get("Goals Conceded")),
            row("Save %", f"{(player['saves'] / max(1, player['saves'] + player['goals_conceded']) * 100):.1f}%")
        ]
    elif position == "DEF":
        metrics = [
            row("Clean Sheets", player["clean_sheets"], position_rankings.get("Clean Sheets")),
            row("Goals", player["goals_scored"], position_rankings.get("Goals")),
            row("Assists", player["assists"], position_rankings.get("Assists")),
            row("Goals Conceded", player["goals_conceded"], position_rankings.get("Goals Conceded")),
            row("Goal Involvement", player["goals_scored"] + player["assists"])
        ]
        # Add Expected Goals and Expected Assists for defenders
        if "expected_goals" in player and pd.notna(player["expected_goals"]):
            metrics.append(row("Expected Goals (xG)", f"{player['expected_goals']:.2f}"))
        if "expected_assists" in player and pd.notna(player["expected_assists"]):
            metrics.append(row("Expected Assists (xA)", f"{player['expected_assists']:.2f}"))
    else:
        metrics = [
            row("Goals", player["goals_scored"], position_rankings.get("Goals")),
            row("Assists", player["assists"], position_rankings.get("Assists")),
            row("Goal Involvement", player["goals_scored"] + player["assists"]),
            row("Goals per 90", f"{(player['goals_scored'] / max(1, player['minutes']) * 90):.2f}")
        ]
        # Add Expected Goals and Expected Assists for midfielders and forwards
        if "expected_goals" in player and pd.notna(player["expected_goals"]):
            metrics.append(row("Expected Goals (xG)", f"{player['expected_goals']:.2f}"))
        if "expected_assists" in player and pd.notna(player["expected_assists"]):
            metrics.append(row("Expected Assists (xA)", f"{player['expected_assists']:.2f}"))
    sections["Performance Metrics"] = pd.DataFrame(metrics)

    # Advanced Metrics
    advanced = []
    if "expected_goals" in player and pd.notna(player["expected_goals"]):
        xg_diff = player["goals_scored"] - player["expected_goals"]
        advanced.append(row("xG Overperformance", f"{xg_diff:+.2f}"))
    if "expected_assists" in player and pd.notna(player["expected_assists"]):
        xa_diff = player["assists"] - player["expected_assists"]
        advanced.append(row("xA Overperformance", f"{xa_diff:+.2f}"))
    if advanced:
        sections["Advanced Metrics"] = pd.DataFrame(advanced)

    # ICT Index
    sections["ICT Index Breakdown"] = pd.DataFrame([
        row("Influence", f"{player['influence']:.1f}", position_rankings.get("Influence")),
        row("Creativity", f"{player['creativity']:.1f}", position_rankings.get("Creativity")),
        row("Threat", f"{player['threat']:.1f}", position_rankings.get("Threat")),
        row("ICT Total", f"{player['ict_index']:.1f}", position_rankings.get("ICT Index"))
    ])

    # Disciplinary
    sections["Disciplinary"] = pd.DataFrame([
        row("Yellow Cards", player["yellow_cards"], position_rankings.get("Yellow Cards")),
        row("Red Cards", player["red_cards"], position_rankings.get("Red Cards")),
    ])

    # Availability
    status_map = {
        'a': '✅ Available',
        'd': '🤕 Doubtful', 
        'i': '🏥 Injured',
        's': '⏸️ Suspended',
        'u': '❓ Unavailable'
    }
    status = status_map.get(player.get("status", "a"), "❓ Unknown")
    sections["Availability"] = pd.DataFrame([
        row("Status", status),
        row("Chance of Playing", f"{player.get('chance_of_playing_next_round', 100)}%"),
        row("News", player.get("news", "No current news"))
    ])

    # Fixture Outlook
    if "avg_fixture_difficulty_5" in player:
        sections["Fixture Outlook"] = pd.DataFrame([
            row("Next 5 GWs Difficulty", f"{player['avg_fixture_difficulty_5']:.1f}/5"),
            row("Next 10 GWs Difficulty", f"{player.get('avg_fixture_difficulty_10', 'N/A')}/5")
        ])

    return sections

@tool
def find_player_replacements(player_name: str, key_attributes: dict, price_tolerance: float = 1.0, max_suggestions: int = 3) -> str:
    """
    Find replacement players based on specified key attributes using search_players.
    The AI should analyze the target player first and provide key attributes to search for.
    IMPORTANT: Always use get_player_details first for the player to be replaced.
    Args:
        player_name: Name of the player to find replacements for (used for display)
        key_attributes: Dictionary of key attributes with their values, e.g.:
                       {"position": "MID", "min_price": 7.0, "max_price": 9.0, 
                        "min_total_points": 80, "min_form": 4.0}
        price_tolerance: Maximum price difference in millions (default: 1.0) - used if no price range in key_attributes
        max_suggestions: Number of replacement suggestions to return (default: 3)
    
    Returns:
        String with player replacement suggestions based on the specified key attributes
    """
    try:
        # Use key_attributes directly as search parameters
        search_params = key_attributes.copy()
        
        # Ensure we have basic required parameters
        if 'position' not in search_params:
            return "Error: 'position' must be included in key_attributes to find replacements."
        
        # Set price range if not provided in key_attributes
        if 'min_price' not in search_params and 'max_price' not in search_params:
            if 'price' in search_params:
                target_price = search_params['price']
                search_params['min_price'] = max(0, target_price - price_tolerance)
                search_params['max_price'] = target_price + price_tolerance
                del search_params['price']  # Remove target price, keep range
        
        # Use search_players to find candidates
        search_results = search_players(
            limit=max_suggestions,
            sort_by="total_points",
            ascending=False,
            filters=search_params
        )
        
        if "No players found" in search_results or "Error" in search_results:
            # Fallback with just position and price range
            fallback_filters = {}
            if 'position' in search_params:
                fallback_filters['position'] = search_params['position']
            if 'min_price' in search_params:
                fallback_filters['min_price'] = search_params['min_price']
            if 'max_price' in search_params:
                fallback_filters['max_price'] = search_params['max_price']
                
            search_results = search_players(
                limit=max_suggestions,
                sort_by="total_points",
                ascending=False,
                filters=fallback_filters
            )
        
        # Format the replacement analysis
        result_lines = []
        result_lines.append(f"🔄 Player Replacement Analysis for {player_name}")
        result_lines.append(f"📍 Position: {search_params.get('position', 'Unknown')}")
        
        # Show price range if available
        if 'min_price' in search_params or 'max_price' in search_params:
            min_p = search_params.get('min_price', 0)
            max_p = search_params.get('max_price', 'unlimited')
            result_lines.append(f"💰 Price Range: £{min_p:.1f}m - £{max_p}m" if max_p != 'unlimited' else f"💰 Price Range: £{min_p:.1f}m+")
        
        result_lines.append("")
        result_lines.append("🎯 Search Criteria Used:")
        
        # List the key attributes used in search
        criteria_used = []
        for key, value in search_params.items():
            if key == 'position':
                criteria_used.append(f"Position: {value}")
            elif key.startswith('min_'):
                attr_name = key[4:].replace('_', ' ').title()
                criteria_used.append(f"Min {attr_name}: {value}")
            elif key.startswith('max_'):
                attr_name = key[4:].replace('_', ' ').title()
                criteria_used.append(f"Max {attr_name}: {value}")
        
        if criteria_used:
            result_lines.append("   • " + "\n   • ".join(criteria_used))
        
        result_lines.append("")
        
        if "No players found" in search_results:
            result_lines.append("❌ No suitable replacements found with the specified criteria.")
            result_lines.append("💡 Consider relaxing some of the key_attributes for more options.")
        else:
            result_lines.append("🎯 Replacement Suggestions:")
            result_lines.append("")
            result_lines.append(search_results)
        
        return "\n".join(result_lines)
        
    except Exception as e:
        return f"Error finding player replacements: {str(e)}"