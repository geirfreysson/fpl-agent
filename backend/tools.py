import pandas as pd
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

@tool
def search_players(
    limit: float = 10,
    sort_by: str = "total_points",
    ascending: bool = False,
    # Player Identity
    player_id: float = None,
    first_name: str = None,
    second_name: str = None,
    web_name: str = None,
    position: str = None,  # goalkeeper, defender, midfielder, forward
    
    # Team Information
    team: str = None,
    status: str = None,  # available, injured, etc.
    
    # Cost & Ownership
    min_price: float = None,
    max_price: float = None,
    min_cost_change_start: int = None,
    max_cost_change_start: int = None,
    min_ownership: float = None,
    max_ownership: float = None,
    
    # Performance Stats
    min_total_points: float = None,
    max_total_points: float = None,
    min_event_points: float = None,
    max_event_points: float = None,
    min_form: float = None,
    max_form: float = None,
    min_points_per_game: float = None,
    max_points_per_game: float = None,
    min_minutes: float = None,
    max_minutes: float = None,
    min_goals_scored: float = None,
    max_goals_scored: float = None,
    min_assists: float = None,
    max_assists: float = None,
    min_clean_sheets: float = None,
    max_clean_sheets: float = None,
    min_goals_conceded: float = None,
    max_goals_conceded: float = None,
    min_saves: float = None,
    max_saves: float = None,
    min_bonus: float = None,
    max_bonus: float = None,
    min_bps: float = None,
    max_bps: float = None,
    
    # Advanced Metrics
    min_influence: float = None,
    max_influence: float = None,
    min_creativity: float = None,
    max_creativity: float = None,
    min_threat: float = None,
    max_threat: float = None,
    min_ict_index: float = None,
    max_ict_index: float = None,
    min_expected_goals: float = None,
    max_expected_goals: float = None,
    min_expected_assists: float = None,
    max_expected_assists: float = None,
    min_expected_goal_involvements: float = None,
    max_expected_goal_involvements: float = None,
    min_expected_goals_conceded: float = None,
    max_expected_goals_conceded: float = None,
    
    # === NEW ENHANCED FEATURES ===
    # Value Metrics
    min_points_per_million: float = None,
    max_points_per_million: float = None,
    min_form_per_million: float = None,
    max_form_per_million: float = None,
    min_expected_goals_per_million: float = None,
    max_expected_goals_per_million: float = None,
    
    # Performance Efficiency
    min_minutes_per_game: float = None,
    max_minutes_per_game: float = None,
    min_points_per_minute: float = None,
    max_points_per_minute: float = None,
    min_goal_involvement_rate: float = None,
    max_goal_involvement_rate: float = None,
    
    # Expected vs Actual Performance
    min_goals_overperformance: float = None,
    max_goals_overperformance: float = None,
    min_assists_overperformance: float = None,
    max_assists_overperformance: float = None,
    min_goals_luck_factor: float = None,
    max_goals_luck_factor: float = None,
    min_assists_luck_factor: float = None,
    max_assists_luck_factor: float = None,
    
    # Consistency & Transfer Metrics
    min_form_consistency: float = None,
    max_form_consistency: float = None,
    min_transfer_momentum: int = None,
    max_transfer_momentum: int = None,
    ownership_category: str = None,  # Low, Medium, High, Template
    
    # Position-Specific Features
    min_save_percentage: float = None,  # Goalkeepers
    max_save_percentage: float = None,
    min_clean_sheet_rate: float = None,  # GK/Defenders
    max_clean_sheet_rate: float = None,
    min_defensive_value: float = None,  # Defenders
    max_defensive_value: float = None,
    min_attacking_threat: float = None,  # Mid/Forwards
    max_attacking_threat: float = None,
    
    # Fixture Difficulty
    min_avg_fixture_difficulty_3: float = None,
    max_avg_fixture_difficulty_3: float = None,
    min_avg_fixture_difficulty_5: float = None,
    max_avg_fixture_difficulty_5: float = None,
    min_avg_fixture_difficulty_10: float = None,
    max_avg_fixture_difficulty_10: float = None,
    min_home_fixture_difficulty_5: float = None,
    max_home_fixture_difficulty_5: float = None,
    min_away_fixture_difficulty_5: float = None,
    max_away_fixture_difficulty_5: float = None,
    
    # Ranking Features
    min_points_rank_in_position: int = None,
    max_points_rank_in_position: int = None,
    min_value_rank_in_position: int = None,
    max_value_rank_in_position: int = None,
    min_form_rank_in_position: int = None,
    max_form_rank_in_position: int = None,
    
    # Availability  
    min_chance_of_playing: float = None,
    max_chance_of_playing: float = None,
    
    # High-Value FPL Features
    is_penalty_taker: bool = None,
    is_corner_taker: bool = None,
    is_freekick_taker: bool = None,
    min_captain_potential: float = None,
    max_captain_potential: float = None,
    min_goals_per_90: float = None,
    max_goals_per_90: float = None,
    min_assists_per_90: float = None,
    max_assists_per_90: float = None,
    budget_enabler_price: float = None  # Exact price match for budget planning
) -> str:
    """
    Search for players with comprehensive filtering options including enhanced features. Returns players matching all specified filters.
    
    Args:
        limit: Number of players to return (default: 10)
        sort_by: Column to sort results by (default: "total_points"). Common options:
            - Performance: "total_points", "form", "points_per_game", "event_points"
            - Value: "points_per_million", "form_per_million", "now_cost"
            - Expected: "expected_goals", "expected_assists", "expected_goal_involvements"
            - Enhanced: "points_per_minute", "goal_involvement_rate", "attacking_threat"
            - Fixture: "avg_fixture_difficulty_3", "avg_fixture_difficulty_5"
            - Consistency: "form_consistency", "transfer_momentum"
            - Position rank: "points_rank_in_position", "value_rank_in_position"
        ascending: Sort direction - False for highest first (default), True for lowest first
        
        # Player Identity
        player_id: Specific player ID
        first_name: Filter by first name (partial match)
        second_name: Filter by second name (partial match)
        web_name: Filter by display name (partial match)
        position: Filter by position ("goalkeeper", "defender", "midfielder", "forward")
        team: Filter by team name (partial match)
        status: Filter by player status ("available", "injured", etc.)
        
        # Cost & Ownership
        min_price: Minimum price in millions (e.g., 4.0 for £4.0m)
        max_price: Maximum price in millions (e.g., 15.0 for £15.0m)
        min_cost_change_start: Minimum price change since season start
        max_cost_change_start: Maximum price change since season start
        min_ownership: Minimum ownership percentage
        max_ownership: Maximum ownership percentage
        
        # Performance Stats
        min_total_points: Minimum total FPL points
        max_total_points: Maximum total FPL points
        min_event_points: Minimum latest gameweek points
        max_event_points: Maximum latest gameweek points
        min_form: Minimum form (avg points last 5 games)
        max_form: Maximum form (avg points last 5 games)
        min_points_per_game: Minimum points per game
        max_points_per_game: Maximum points per game
        min_minutes: Minimum minutes played
        max_minutes: Maximum minutes played
        min_goals_scored: Minimum goals scored
        max_goals_scored: Maximum goals scored
        min_assists: Minimum assists
        max_assists: Maximum assists
        min_clean_sheets: Minimum clean sheets
        max_clean_sheets: Maximum clean sheets
        min_goals_conceded: Minimum goals conceded
        max_goals_conceded: Maximum goals conceded
        min_saves: Minimum saves made
        max_saves: Maximum saves made
        min_bonus: Minimum bonus points
        max_bonus: Maximum bonus points
        min_bps: Minimum bonus points system score
        max_bps: Maximum bonus points system score
        
        # Advanced Metrics
        min_influence: Minimum influence rating
        max_influence: Maximum influence rating
        min_creativity: Minimum creativity rating
        max_creativity: Maximum creativity rating
        min_threat: Minimum threat rating
        max_threat: Maximum threat rating
        min_ict_index: Minimum ICT index
        max_ict_index: Maximum ICT index
        min_expected_goals: Minimum expected goals
        max_expected_goals: Maximum expected goals
        min_expected_assists: Minimum expected assists
        max_expected_assists: Maximum expected assists
        min_expected_goal_involvements: Minimum expected goal involvements
        max_expected_goal_involvements: Maximum expected goal involvements
        min_expected_goals_conceded: Minimum expected goals conceded
        max_expected_goals_conceded: Maximum expected goals conceded
        
        # === ENHANCED FEATURES ===
        # Value Metrics
        min_points_per_million: Minimum points per million spent
        max_points_per_million: Maximum points per million spent
        min_form_per_million: Minimum form per million spent
        max_form_per_million: Maximum form per million spent
        min_expected_goals_per_million: Minimum expected goals per million
        max_expected_goals_per_million: Maximum expected goals per million
        
        # Performance Efficiency
        min_minutes_per_game: Minimum minutes per game (nailed-on status)
        max_minutes_per_game: Maximum minutes per game
        min_points_per_minute: Minimum points per minute played
        max_points_per_minute: Maximum points per minute played
        min_goal_involvement_rate: Minimum goal involvement rate
        max_goal_involvement_rate: Maximum goal involvement rate
        
        # Expected vs Actual Performance
        min_goals_overperformance: Minimum goals vs expected goals difference
        max_goals_overperformance: Maximum goals vs expected goals difference
        min_assists_overperformance: Minimum assists vs expected assists difference
        max_assists_overperformance: Maximum assists vs expected assists difference
        min_goals_luck_factor: Minimum goals luck factor (sustainability)
        max_goals_luck_factor: Maximum goals luck factor
        min_assists_luck_factor: Minimum assists luck factor
        max_assists_luck_factor: Maximum assists luck factor
        
        # Consistency & Transfer Metrics
        min_form_consistency: Minimum form consistency score
        max_form_consistency: Maximum form consistency score
        min_transfer_momentum: Minimum transfer momentum (net transfers)
        max_transfer_momentum: Maximum transfer momentum
        ownership_category: Filter by ownership category ("Low", "Medium", "High", "Template")
        
        # Position-Specific Features
        min_save_percentage: Minimum save percentage (Goalkeepers)
        max_save_percentage: Maximum save percentage
        min_clean_sheet_rate: Minimum clean sheet rate (GK/Defenders)
        max_clean_sheet_rate: Maximum clean sheet rate
        min_defensive_value: Minimum defensive value score (Defenders)
        max_defensive_value: Maximum defensive value score
        min_attacking_threat: Minimum attacking threat score (Mid/Forwards)
        max_attacking_threat: Maximum attacking threat score
        
        # Fixture Difficulty Analysis
        min_avg_fixture_difficulty_3: Minimum average fixture difficulty (next 3 games)
        max_avg_fixture_difficulty_3: Maximum average fixture difficulty (next 3 games)
        min_avg_fixture_difficulty_5: Minimum average fixture difficulty (next 5 games)
        max_avg_fixture_difficulty_5: Maximum average fixture difficulty (next 5 games)
        min_avg_fixture_difficulty_10: Minimum average fixture difficulty (next 10 games)
        max_avg_fixture_difficulty_10: Maximum average fixture difficulty (next 10 games)
        min_home_fixture_difficulty_5: Minimum home fixture difficulty (next 5 home games)
        max_home_fixture_difficulty_5: Maximum home fixture difficulty (next 5 home games)
        min_away_fixture_difficulty_5: Minimum away fixture difficulty (next 5 away games)
        max_away_fixture_difficulty_5: Maximum away fixture difficulty (next 5 away games)
        
        # Position Rankings
        min_points_rank_in_position: Minimum points rank within position
        max_points_rank_in_position: Maximum points rank within position
        min_value_rank_in_position: Minimum value rank within position
        max_value_rank_in_position: Maximum value rank within position
        min_form_rank_in_position: Minimum form rank within position
        max_form_rank_in_position: Maximum form rank within position
        
        # Availability
        min_chance_of_playing: Minimum injury probability (0-100)
        max_chance_of_playing: Maximum injury probability (0-100)
        
        # High-Value FPL Features
        is_penalty_taker: Filter penalty takers (True/False)
        is_corner_taker: Filter corner takers (True/False) 
        is_freekick_taker: Filter free kick takers (True/False)
        min_captain_potential: Minimum captain potential score (combination of ceiling + consistency)
        max_captain_potential: Maximum captain potential score
        min_goals_per_90: Minimum goals per 90 minutes (rate stat for rotation players)
        max_goals_per_90: Maximum goals per 90 minutes
        min_assists_per_90: Minimum assists per 90 minutes
        max_assists_per_90: Maximum assists per 90 minutes
        budget_enabler_price: Exact price match for budget planning (e.g., 4.5 for £4.5m enablers)
    
    Returns:
        String with players matching the criteria and filters, sorted by specified metric
        
    Examples for AI agent:
        # Get top scorers
        search_players(sort_by="total_points", limit=5)
        
        # Best value midfielders under £8m
        search_players(position="midfielder", max_price=8.0, sort_by="points_per_million", limit=10)
        
        # Penalty takers under £10m with good fixtures
        search_players(is_penalty_taker=True, max_price=10.0, max_avg_fixture_difficulty_5=3.0)
        
        # High captain potential players 
        search_players(sort_by="captain_potential", min_minutes=500, limit=8)
        
        # Budget enablers at exactly £4.5m
        search_players(budget_enabler_price=4.5, min_minutes_per_game=60)
        
        # Set piece takers with good goal rates
        search_players(is_corner_taker=True, min_goals_per_90=0.3, sort_by="goals_per_90")
    """
    try:
        # Get the project root directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        
        # Construct absolute paths to data files
        elements_path = os.path.join(project_root, 'fpl_data', 'fpl_data', 'elements.parquet')
        teams_path = os.path.join(project_root, 'fpl_data', 'fpl_data', 'teams.json')
        
        # Base columns always needed (including total_points for default sorting)
        base_columns = ['id', 'web_name', 'first_name', 'second_name', 'team', 'element_type', 'now_cost', 'total_points']
        columns_to_load = base_columns.copy()
        
        # Add columns needed for filtering
        filter_columns = {
            # Player Identity (already in base)
            
            # Team Information
            'status': status,
            
            # Cost & Ownership
            'cost_change_start': any([min_cost_change_start, max_cost_change_start]),
            'selected_by_percent': any([min_ownership, max_ownership]),
            
            # Performance Stats
            'total_points': any([min_total_points, max_total_points]),
            'event_points': any([min_event_points, max_event_points]),
            'form': any([min_form, max_form]),
            'points_per_game': any([min_points_per_game, max_points_per_game]),
            'minutes': any([min_minutes, max_minutes]),
            'goals_scored': any([min_goals_scored, max_goals_scored]),
            'assists': any([min_assists, max_assists]),
            'clean_sheets': any([min_clean_sheets, max_clean_sheets]),
            'goals_conceded': any([min_goals_conceded, max_goals_conceded]),
            'saves': any([min_saves, max_saves]),
            'bonus': any([min_bonus, max_bonus]),
            'bps': any([min_bps, max_bps]),
            
            # Advanced Metrics
            'influence': any([min_influence, max_influence]),
            'creativity': any([min_creativity, max_creativity]),
            'threat': any([min_threat, max_threat]),
            'ict_index': any([min_ict_index, max_ict_index]),
            'expected_goals': any([min_expected_goals, max_expected_goals]),
            'expected_assists': any([min_expected_assists, max_expected_assists]),
            'expected_goal_involvements': any([min_expected_goal_involvements, max_expected_goal_involvements]),
            'expected_goals_conceded': any([min_expected_goals_conceded, max_expected_goals_conceded]),
            
            # Enhanced Value Metrics
            'points_per_million': any([min_points_per_million, max_points_per_million]),
            'form_per_million': any([min_form_per_million, max_form_per_million]),
            'expected_goals_per_million': any([min_expected_goals_per_million, max_expected_goals_per_million]),
            
            # Performance Efficiency
            'minutes_per_game': any([min_minutes_per_game, max_minutes_per_game]),
            'points_per_minute': any([min_points_per_minute, max_points_per_minute]),
            'goal_involvement_rate': any([min_goal_involvement_rate, max_goal_involvement_rate]),
            
            # Expected vs Actual
            'goals_overperformance': any([min_goals_overperformance, max_goals_overperformance]),
            'assists_overperformance': any([min_assists_overperformance, max_assists_overperformance]),
            'goals_luck_factor': any([min_goals_luck_factor, max_goals_luck_factor]),
            'assists_luck_factor': any([min_assists_luck_factor, max_assists_luck_factor]),
            
            # Consistency & Transfer Metrics
            'form_consistency': any([min_form_consistency, max_form_consistency]),
            'transfer_momentum': any([min_transfer_momentum, max_transfer_momentum]),
            'ownership_category': ownership_category,
            
            # Position-Specific Features
            'save_percentage': any([min_save_percentage, max_save_percentage]),
            'clean_sheet_rate': any([min_clean_sheet_rate, max_clean_sheet_rate]),
            'defensive_value': any([min_defensive_value, max_defensive_value]),
            'attacking_threat': any([min_attacking_threat, max_attacking_threat]),
            
            # Fixture Difficulty Analysis
            'avg_fixture_difficulty_3': any([min_avg_fixture_difficulty_3, max_avg_fixture_difficulty_3]),
            'avg_fixture_difficulty_5': any([min_avg_fixture_difficulty_5, max_avg_fixture_difficulty_5]),
            'avg_fixture_difficulty_10': any([min_avg_fixture_difficulty_10, max_avg_fixture_difficulty_10]),
            'home_fixture_difficulty_5': any([min_home_fixture_difficulty_5, max_home_fixture_difficulty_5]),
            'away_fixture_difficulty_5': any([min_away_fixture_difficulty_5, max_away_fixture_difficulty_5]),
            
            # Position Rankings
            'points_rank_in_position': any([min_points_rank_in_position, max_points_rank_in_position]),
            'value_rank_in_position': any([min_value_rank_in_position, max_value_rank_in_position]),
            'form_rank_in_position': any([min_form_rank_in_position, max_form_rank_in_position]),
            
            # Availability
            'chance_of_playing_next_round': any([min_chance_of_playing, max_chance_of_playing])
        }
        
        # Add needed columns to load list
        for col, needed in filter_columns.items():
            if needed and col not in columns_to_load:
                columns_to_load.append(col)
        
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
        
        # Convert string columns to numeric for any loaded columns that need it
        numeric_columns = ['form', 'points_per_game', 'creativity', 'threat', 'influence', 
                          'ict_index', 'expected_goals', 'expected_assists', 'expected_goal_involvements']
        for col in numeric_columns:
            if col in players_df.columns:
                players_df[col] = pd.to_numeric(players_df[col], errors='coerce')
        
        # Apply filters
        filtered_players = players_df.copy()
        
        # Helper function to convert string columns to numeric
        def convert_to_numeric(df, column):
            if column in df.columns:
                df[column] = pd.to_numeric(df[column], errors='coerce')
            return df
        
        # Player Identity filters
        if player_id is not None:
            filtered_players = filtered_players[filtered_players['id'] == player_id]
        if first_name:
            filtered_players = filtered_players[filtered_players['first_name'].str.contains(first_name, case=False, na=False)]
        if second_name:
            filtered_players = filtered_players[filtered_players['second_name'].str.contains(second_name, case=False, na=False)]
        if web_name:
            filtered_players = filtered_players[filtered_players['web_name'].str.contains(web_name, case=False, na=False)]
        
        # Position filter
        if position:
            position_map = {
                'goalkeeper': 1, 'gk': 1,
                'defender': 2, 'def': 2, 'defence': 2,
                'midfielder': 3, 'mid': 3, 'midfield': 3,
                'forward': 4, 'fwd': 4, 'attack': 4, 'attacker': 4
            }
            position_id = position_map.get(position.lower())
            if position_id:
                filtered_players = filtered_players[filtered_players['element_type'] == position_id]
            else:
                return f"Invalid position '{position}'. Use: goalkeeper, defender, midfielder, or forward"
        
        # Team Information filters
        if team:
            # Find team ID by name (case insensitive)
            team_id = None
            for tid, tname in team_lookup.items():
                if team.lower() in tname.lower() or tname.lower() in team.lower():
                    team_id = tid
                    break
            if team_id:
                filtered_players = filtered_players[filtered_players['team'] == team_id]
            else:
                available_teams = ', '.join(sorted(team_lookup.values()))
                return f"Team '{team}' not found. Available teams: {available_teams}"
        
        if status:
            filtered_players = filtered_players[filtered_players['status'].str.contains(status, case=False, na=False)]
        
        # Cost & Ownership filters
        if min_price is not None:
            filtered_players = filtered_players[filtered_players['now_cost'] >= min_price * 10]
        if max_price is not None:
            filtered_players = filtered_players[filtered_players['now_cost'] <= max_price * 10]
        if min_cost_change_start is not None:
            filtered_players = filtered_players[filtered_players['cost_change_start'] >= min_cost_change_start]
        if max_cost_change_start is not None:
            filtered_players = filtered_players[filtered_players['cost_change_start'] <= max_cost_change_start]
        if min_ownership is not None:
            filtered_players = convert_to_numeric(filtered_players, 'selected_by_percent')
            filtered_players = filtered_players[filtered_players['selected_by_percent'] >= min_ownership]
        if max_ownership is not None:
            filtered_players = convert_to_numeric(filtered_players, 'selected_by_percent')
            filtered_players = filtered_players[filtered_players['selected_by_percent'] <= max_ownership]
        
        # Performance Stats filters
        if min_total_points is not None:
            filtered_players = filtered_players[filtered_players['total_points'] >= min_total_points]
        if max_total_points is not None:
            filtered_players = filtered_players[filtered_players['total_points'] <= max_total_points]
        if min_event_points is not None:
            filtered_players = filtered_players[filtered_players['event_points'] >= min_event_points]
        if max_event_points is not None:
            filtered_players = filtered_players[filtered_players['event_points'] <= max_event_points]
        if min_form is not None:
            filtered_players = convert_to_numeric(filtered_players, 'form')
            filtered_players = filtered_players[filtered_players['form'] >= min_form]
        if max_form is not None:
            filtered_players = convert_to_numeric(filtered_players, 'form')
            filtered_players = filtered_players[filtered_players['form'] <= max_form]
        if min_points_per_game is not None:
            filtered_players = convert_to_numeric(filtered_players, 'points_per_game')
            filtered_players = filtered_players[filtered_players['points_per_game'] >= min_points_per_game]
        if max_points_per_game is not None:
            filtered_players = convert_to_numeric(filtered_players, 'points_per_game')
            filtered_players = filtered_players[filtered_players['points_per_game'] <= max_points_per_game]
        if min_minutes is not None:
            filtered_players = filtered_players[filtered_players['minutes'] >= min_minutes]
        if max_minutes is not None:
            filtered_players = filtered_players[filtered_players['minutes'] <= max_minutes]
        if min_goals_scored is not None:
            filtered_players = filtered_players[filtered_players['goals_scored'] >= min_goals_scored]
        if max_goals_scored is not None:
            filtered_players = filtered_players[filtered_players['goals_scored'] <= max_goals_scored]
        if min_assists is not None:
            filtered_players = filtered_players[filtered_players['assists'] >= min_assists]
        if max_assists is not None:
            filtered_players = filtered_players[filtered_players['assists'] <= max_assists]
        if min_clean_sheets is not None:
            filtered_players = filtered_players[filtered_players['clean_sheets'] >= min_clean_sheets]
        if max_clean_sheets is not None:
            filtered_players = filtered_players[filtered_players['clean_sheets'] <= max_clean_sheets]
        if min_goals_conceded is not None:
            filtered_players = filtered_players[filtered_players['goals_conceded'] >= min_goals_conceded]
        if max_goals_conceded is not None:
            filtered_players = filtered_players[filtered_players['goals_conceded'] <= max_goals_conceded]
        if min_saves is not None:
            filtered_players = filtered_players[filtered_players['saves'] >= min_saves]
        if max_saves is not None:
            filtered_players = filtered_players[filtered_players['saves'] <= max_saves]
        if min_bonus is not None:
            filtered_players = filtered_players[filtered_players['bonus'] >= min_bonus]
        if max_bonus is not None:
            filtered_players = filtered_players[filtered_players['bonus'] <= max_bonus]
        if min_bps is not None:
            filtered_players = filtered_players[filtered_players['bps'] >= min_bps]
        if max_bps is not None:
            filtered_players = filtered_players[filtered_players['bps'] <= max_bps]
        
        # Advanced Metrics filters
        if min_influence is not None:
            filtered_players = convert_to_numeric(filtered_players, 'influence')
            filtered_players = filtered_players[filtered_players['influence'] >= min_influence]
        if max_influence is not None:
            filtered_players = convert_to_numeric(filtered_players, 'influence')
            filtered_players = filtered_players[filtered_players['influence'] <= max_influence]
        if min_creativity is not None:
            filtered_players = convert_to_numeric(filtered_players, 'creativity')
            filtered_players = filtered_players[filtered_players['creativity'] >= min_creativity]
        if max_creativity is not None:
            filtered_players = convert_to_numeric(filtered_players, 'creativity')
            filtered_players = filtered_players[filtered_players['creativity'] <= max_creativity]
        if min_threat is not None:
            filtered_players = convert_to_numeric(filtered_players, 'threat')
            filtered_players = filtered_players[filtered_players['threat'] >= min_threat]
        if max_threat is not None:
            filtered_players = convert_to_numeric(filtered_players, 'threat')
            filtered_players = filtered_players[filtered_players['threat'] <= max_threat]
        if min_ict_index is not None:
            filtered_players = convert_to_numeric(filtered_players, 'ict_index')
            filtered_players = filtered_players[filtered_players['ict_index'] >= min_ict_index]
        if max_ict_index is not None:
            filtered_players = convert_to_numeric(filtered_players, 'ict_index')
            filtered_players = filtered_players[filtered_players['ict_index'] <= max_ict_index]
        if min_expected_goals is not None:
            filtered_players = convert_to_numeric(filtered_players, 'expected_goals')
            filtered_players = filtered_players[filtered_players['expected_goals'] >= min_expected_goals]
        if max_expected_goals is not None:
            filtered_players = convert_to_numeric(filtered_players, 'expected_goals')
            filtered_players = filtered_players[filtered_players['expected_goals'] <= max_expected_goals]
        if min_expected_assists is not None:
            filtered_players = convert_to_numeric(filtered_players, 'expected_assists')
            filtered_players = filtered_players[filtered_players['expected_assists'] >= min_expected_assists]
        if max_expected_assists is not None:
            filtered_players = convert_to_numeric(filtered_players, 'expected_assists')
            filtered_players = filtered_players[filtered_players['expected_assists'] <= max_expected_assists]
        if min_expected_goal_involvements is not None:
            filtered_players = convert_to_numeric(filtered_players, 'expected_goal_involvements')
            filtered_players = filtered_players[filtered_players['expected_goal_involvements'] >= min_expected_goal_involvements]
        if max_expected_goal_involvements is not None:
            filtered_players = convert_to_numeric(filtered_players, 'expected_goal_involvements')
            filtered_players = filtered_players[filtered_players['expected_goal_involvements'] <= max_expected_goal_involvements]
        if min_expected_goals_conceded is not None:
            filtered_players = convert_to_numeric(filtered_players, 'expected_goals_conceded')
            filtered_players = filtered_players[filtered_players['expected_goals_conceded'] >= min_expected_goals_conceded]
        if max_expected_goals_conceded is not None:
            filtered_players = convert_to_numeric(filtered_players, 'expected_goals_conceded')
            filtered_players = filtered_players[filtered_players['expected_goals_conceded'] <= max_expected_goals_conceded]
        
        # === ENHANCED FEATURES FILTERS ===
        # Value Metrics filters
        if min_points_per_million is not None:
            filtered_players = convert_to_numeric(filtered_players, 'points_per_million')
            filtered_players = filtered_players[filtered_players['points_per_million'] >= min_points_per_million]
        if max_points_per_million is not None:
            filtered_players = convert_to_numeric(filtered_players, 'points_per_million')
            filtered_players = filtered_players[filtered_players['points_per_million'] <= max_points_per_million]
        if min_form_per_million is not None:
            filtered_players = convert_to_numeric(filtered_players, 'form_per_million')
            filtered_players = filtered_players[filtered_players['form_per_million'] >= min_form_per_million]
        if max_form_per_million is not None:
            filtered_players = convert_to_numeric(filtered_players, 'form_per_million')
            filtered_players = filtered_players[filtered_players['form_per_million'] <= max_form_per_million]
        if min_expected_goals_per_million is not None:
            filtered_players = convert_to_numeric(filtered_players, 'expected_goals_per_million')
            filtered_players = filtered_players[filtered_players['expected_goals_per_million'] >= min_expected_goals_per_million]
        if max_expected_goals_per_million is not None:
            filtered_players = convert_to_numeric(filtered_players, 'expected_goals_per_million')
            filtered_players = filtered_players[filtered_players['expected_goals_per_million'] <= max_expected_goals_per_million]
        
        # Performance Efficiency filters
        if min_minutes_per_game is not None:
            filtered_players = convert_to_numeric(filtered_players, 'minutes_per_game')
            filtered_players = filtered_players[filtered_players['minutes_per_game'] >= min_minutes_per_game]
        if max_minutes_per_game is not None:
            filtered_players = convert_to_numeric(filtered_players, 'minutes_per_game')
            filtered_players = filtered_players[filtered_players['minutes_per_game'] <= max_minutes_per_game]
        if min_points_per_minute is not None:
            filtered_players = convert_to_numeric(filtered_players, 'points_per_minute')
            filtered_players = filtered_players[filtered_players['points_per_minute'] >= min_points_per_minute]
        if max_points_per_minute is not None:
            filtered_players = convert_to_numeric(filtered_players, 'points_per_minute')
            filtered_players = filtered_players[filtered_players['points_per_minute'] <= max_points_per_minute]
        if min_goal_involvement_rate is not None:
            filtered_players = convert_to_numeric(filtered_players, 'goal_involvement_rate')
            filtered_players = filtered_players[filtered_players['goal_involvement_rate'] >= min_goal_involvement_rate]
        if max_goal_involvement_rate is not None:
            filtered_players = convert_to_numeric(filtered_players, 'goal_involvement_rate')
            filtered_players = filtered_players[filtered_players['goal_involvement_rate'] <= max_goal_involvement_rate]
        
        # Expected vs Actual Performance filters
        if min_goals_overperformance is not None:
            filtered_players = convert_to_numeric(filtered_players, 'goals_overperformance')
            filtered_players = filtered_players[filtered_players['goals_overperformance'] >= min_goals_overperformance]
        if max_goals_overperformance is not None:
            filtered_players = convert_to_numeric(filtered_players, 'goals_overperformance')
            filtered_players = filtered_players[filtered_players['goals_overperformance'] <= max_goals_overperformance]
        if min_assists_overperformance is not None:
            filtered_players = convert_to_numeric(filtered_players, 'assists_overperformance')
            filtered_players = filtered_players[filtered_players['assists_overperformance'] >= min_assists_overperformance]
        if max_assists_overperformance is not None:
            filtered_players = convert_to_numeric(filtered_players, 'assists_overperformance')
            filtered_players = filtered_players[filtered_players['assists_overperformance'] <= max_assists_overperformance]
        if min_goals_luck_factor is not None:
            filtered_players = convert_to_numeric(filtered_players, 'goals_luck_factor')
            filtered_players = filtered_players[filtered_players['goals_luck_factor'] >= min_goals_luck_factor]
        if max_goals_luck_factor is not None:
            filtered_players = convert_to_numeric(filtered_players, 'goals_luck_factor')
            filtered_players = filtered_players[filtered_players['goals_luck_factor'] <= max_goals_luck_factor]
        if min_assists_luck_factor is not None:
            filtered_players = convert_to_numeric(filtered_players, 'assists_luck_factor')
            filtered_players = filtered_players[filtered_players['assists_luck_factor'] >= min_assists_luck_factor]
        if max_assists_luck_factor is not None:
            filtered_players = convert_to_numeric(filtered_players, 'assists_luck_factor')
            filtered_players = filtered_players[filtered_players['assists_luck_factor'] <= max_assists_luck_factor]
        
        # Consistency & Transfer Metrics filters
        if min_form_consistency is not None:
            filtered_players = convert_to_numeric(filtered_players, 'form_consistency')
            filtered_players = filtered_players[filtered_players['form_consistency'] >= min_form_consistency]
        if max_form_consistency is not None:
            filtered_players = convert_to_numeric(filtered_players, 'form_consistency')
            filtered_players = filtered_players[filtered_players['form_consistency'] <= max_form_consistency]
        if min_transfer_momentum is not None:
            filtered_players = convert_to_numeric(filtered_players, 'transfer_momentum')
            filtered_players = filtered_players[filtered_players['transfer_momentum'] >= min_transfer_momentum]
        if max_transfer_momentum is not None:
            filtered_players = convert_to_numeric(filtered_players, 'transfer_momentum')
            filtered_players = filtered_players[filtered_players['transfer_momentum'] <= max_transfer_momentum]
        if ownership_category:
            filtered_players = filtered_players[filtered_players['ownership_category'].str.contains(ownership_category, case=False, na=False)]
        
        # Position-Specific Features filters
        if min_save_percentage is not None:
            filtered_players = convert_to_numeric(filtered_players, 'save_percentage')
            filtered_players = filtered_players[filtered_players['save_percentage'] >= min_save_percentage]
        if max_save_percentage is not None:
            filtered_players = convert_to_numeric(filtered_players, 'save_percentage')
            filtered_players = filtered_players[filtered_players['save_percentage'] <= max_save_percentage]
        if min_clean_sheet_rate is not None:
            filtered_players = convert_to_numeric(filtered_players, 'clean_sheet_rate')
            filtered_players = filtered_players[filtered_players['clean_sheet_rate'] >= min_clean_sheet_rate]
        if max_clean_sheet_rate is not None:
            filtered_players = convert_to_numeric(filtered_players, 'clean_sheet_rate')
            filtered_players = filtered_players[filtered_players['clean_sheet_rate'] <= max_clean_sheet_rate]
        if min_defensive_value is not None:
            filtered_players = convert_to_numeric(filtered_players, 'defensive_value')
            filtered_players = filtered_players[filtered_players['defensive_value'] >= min_defensive_value]
        if max_defensive_value is not None:
            filtered_players = convert_to_numeric(filtered_players, 'defensive_value')
            filtered_players = filtered_players[filtered_players['defensive_value'] <= max_defensive_value]
        if min_attacking_threat is not None:
            filtered_players = convert_to_numeric(filtered_players, 'attacking_threat')
            filtered_players = filtered_players[filtered_players['attacking_threat'] >= min_attacking_threat]
        if max_attacking_threat is not None:
            filtered_players = convert_to_numeric(filtered_players, 'attacking_threat')
            filtered_players = filtered_players[filtered_players['attacking_threat'] <= max_attacking_threat]
        
        # Fixture Difficulty filters
        if min_avg_fixture_difficulty_3 is not None:
            filtered_players = convert_to_numeric(filtered_players, 'avg_fixture_difficulty_3')
            filtered_players = filtered_players[filtered_players['avg_fixture_difficulty_3'] >= min_avg_fixture_difficulty_3]
        if max_avg_fixture_difficulty_3 is not None:
            filtered_players = convert_to_numeric(filtered_players, 'avg_fixture_difficulty_3')
            filtered_players = filtered_players[filtered_players['avg_fixture_difficulty_3'] <= max_avg_fixture_difficulty_3]
        if min_avg_fixture_difficulty_5 is not None:
            filtered_players = convert_to_numeric(filtered_players, 'avg_fixture_difficulty_5')
            filtered_players = filtered_players[filtered_players['avg_fixture_difficulty_5'] >= min_avg_fixture_difficulty_5]
        if max_avg_fixture_difficulty_5 is not None:
            filtered_players = convert_to_numeric(filtered_players, 'avg_fixture_difficulty_5')
            filtered_players = filtered_players[filtered_players['avg_fixture_difficulty_5'] <= max_avg_fixture_difficulty_5]
        if min_avg_fixture_difficulty_10 is not None:
            filtered_players = convert_to_numeric(filtered_players, 'avg_fixture_difficulty_10')
            filtered_players = filtered_players[filtered_players['avg_fixture_difficulty_10'] >= min_avg_fixture_difficulty_10]
        if max_avg_fixture_difficulty_10 is not None:
            filtered_players = convert_to_numeric(filtered_players, 'avg_fixture_difficulty_10')
            filtered_players = filtered_players[filtered_players['avg_fixture_difficulty_10'] <= max_avg_fixture_difficulty_10]
        if min_home_fixture_difficulty_5 is not None:
            filtered_players = convert_to_numeric(filtered_players, 'home_fixture_difficulty_5')
            filtered_players = filtered_players[filtered_players['home_fixture_difficulty_5'] >= min_home_fixture_difficulty_5]
        if max_home_fixture_difficulty_5 is not None:
            filtered_players = convert_to_numeric(filtered_players, 'home_fixture_difficulty_5')
            filtered_players = filtered_players[filtered_players['home_fixture_difficulty_5'] <= max_home_fixture_difficulty_5]
        if min_away_fixture_difficulty_5 is not None:
            filtered_players = convert_to_numeric(filtered_players, 'away_fixture_difficulty_5')
            filtered_players = filtered_players[filtered_players['away_fixture_difficulty_5'] >= min_away_fixture_difficulty_5]
        if max_away_fixture_difficulty_5 is not None:
            filtered_players = convert_to_numeric(filtered_players, 'away_fixture_difficulty_5')
            filtered_players = filtered_players[filtered_players['away_fixture_difficulty_5'] <= max_away_fixture_difficulty_5]
        
        # Ranking Features filters
        if min_points_rank_in_position is not None:
            filtered_players = convert_to_numeric(filtered_players, 'points_rank_in_position')
            filtered_players = filtered_players[filtered_players['points_rank_in_position'] >= min_points_rank_in_position]
        if max_points_rank_in_position is not None:
            filtered_players = convert_to_numeric(filtered_players, 'points_rank_in_position')
            filtered_players = filtered_players[filtered_players['points_rank_in_position'] <= max_points_rank_in_position]
        if min_value_rank_in_position is not None:
            filtered_players = convert_to_numeric(filtered_players, 'value_rank_in_position')
            filtered_players = filtered_players[filtered_players['value_rank_in_position'] >= min_value_rank_in_position]
        if max_value_rank_in_position is not None:
            filtered_players = convert_to_numeric(filtered_players, 'value_rank_in_position')
            filtered_players = filtered_players[filtered_players['value_rank_in_position'] <= max_value_rank_in_position]
        if min_form_rank_in_position is not None:
            filtered_players = convert_to_numeric(filtered_players, 'form_rank_in_position')
            filtered_players = filtered_players[filtered_players['form_rank_in_position'] >= min_form_rank_in_position]
        if max_form_rank_in_position is not None:
            filtered_players = convert_to_numeric(filtered_players, 'form_rank_in_position')
            filtered_players = filtered_players[filtered_players['form_rank_in_position'] <= max_form_rank_in_position]
        
        # Availability filters
        if min_chance_of_playing is not None:
            filtered_players = filtered_players[filtered_players['chance_of_playing_next_round'] >= min_chance_of_playing]
        if max_chance_of_playing is not None:
            filtered_players = filtered_players[filtered_players['chance_of_playing_next_round'] <= max_chance_of_playing]
        
        # High-Value FPL Features (Note: These require enhanced data fields)
        # TODO: Implement when data processing adds these derived fields
        if budget_enabler_price is not None:
            # Exact price match for budget planning
            filtered_players = filtered_players[abs(filtered_players['now_cost'] - (budget_enabler_price * 10)) < 1]
        
        # Note: Set piece takers, captain potential, per-90 stats would be filtered here
        # when the corresponding fields are added to the data processing pipeline
        
        # Check if we have any players left after filtering
        if filtered_players.empty:
            return "No players found matching the applied filters."
        
        # Ensure sort column is available in the data
        if sort_by not in filtered_players.columns:
            # Try common alternative column names
            column_aliases = {
                'price': 'now_cost',
                'cost': 'now_cost', 
                'points': 'total_points',
                'xg': 'expected_goals',
                'xa': 'expected_assists',
                'ict': 'ict_index'
            }
            actual_sort_column = column_aliases.get(sort_by.lower(), 'total_points')
            if actual_sort_column not in filtered_players.columns:
                actual_sort_column = 'total_points'  # Final fallback
        else:
            actual_sort_column = sort_by
        
        # Sort and limit results
        limit_int = int(limit) if limit is not None else 10
        sorted_players = filtered_players.sort_values(actual_sort_column, ascending=ascending).head(limit_int)
        
        if sorted_players.empty:
            return "No players found matching the filters."
        
        # Format results
        result_lines = []
        sort_direction = "ascending" if ascending else "descending" 
        result_lines.append(f"Players Found ({len(sorted_players)} results, sorted by {actual_sort_column} {sort_direction}):")
        result_lines.append("")
        
        for rank, (_, player) in enumerate(sorted_players.iterrows(), 1):
            # Build display line with relevant information
            line_parts = [
                f"{rank}. {player['web_name']} ({player['position']})",
                f"{player['team_name']}",
                f"£{player['price_display']:.1f}m"
            ]
            
            # Always show the metrics that were filtered by (user requested data)
            metrics_to_show = []
            
            # Check which filters were applied and show those metrics
            if any([min_total_points, max_total_points]) and 'total_points' in player:
                metrics_to_show.append(f"pts: {int(player['total_points']) if pd.notna(player['total_points']) else 'N/A'}")
            
            if any([min_expected_goals, max_expected_goals]) and 'expected_goals' in player:
                metrics_to_show.append(f"xG: {player['expected_goals']:.1f}" if pd.notna(player['expected_goals']) else "xG: N/A")
            
            if any([min_expected_assists, max_expected_assists]) and 'expected_assists' in player:
                metrics_to_show.append(f"xA: {player['expected_assists']:.1f}" if pd.notna(player['expected_assists']) else "xA: N/A")
            
            if any([min_goals_scored, max_goals_scored]) and 'goals_scored' in player:
                metrics_to_show.append(f"goals: {int(player['goals_scored']) if pd.notna(player['goals_scored']) else 'N/A'}")
            
            if any([min_assists, max_assists]) and 'assists' in player:
                metrics_to_show.append(f"assists: {int(player['assists']) if pd.notna(player['assists']) else 'N/A'}")
            
            if any([min_form, max_form]) and 'form' in player:
                metrics_to_show.append(f"form: {player['form']:.1f}" if pd.notna(player['form']) else "form: N/A")
            
            if any([min_creativity, max_creativity]) and 'creativity' in player:
                metrics_to_show.append(f"creativity: {player['creativity']:.1f}" if pd.notna(player['creativity']) else "creativity: N/A")
            
            if any([min_threat, max_threat]) and 'threat' in player:
                metrics_to_show.append(f"threat: {player['threat']:.1f}" if pd.notna(player['threat']) else "threat: N/A")
            
            if any([min_influence, max_influence]) and 'influence' in player:
                metrics_to_show.append(f"influence: {player['influence']:.1f}" if pd.notna(player['influence']) else "influence: N/A")
            
            if any([min_ict_index, max_ict_index]) and 'ict_index' in player:
                metrics_to_show.append(f"ICT: {player['ict_index']:.1f}" if pd.notna(player['ict_index']) else "ICT: N/A")
            
            if any([min_clean_sheets, max_clean_sheets]) and 'clean_sheets' in player:
                metrics_to_show.append(f"CS: {int(player['clean_sheets']) if pd.notna(player['clean_sheets']) else 'N/A'}")
            
            if any([min_saves, max_saves]) and 'saves' in player:
                metrics_to_show.append(f"saves: {int(player['saves']) if pd.notna(player['saves']) else 'N/A'}")
            
            if any([min_minutes, max_minutes]) and 'minutes' in player:
                metrics_to_show.append(f"mins: {int(player['minutes']) if pd.notna(player['minutes']) else 'N/A'}")
            
            if any([min_ownership, max_ownership]) and 'selected_by_percent' in player:
                metrics_to_show.append(f"owned: {player['selected_by_percent']:.1f}%" if pd.notna(player['selected_by_percent']) else "owned: N/A")
            
            # Add the filtered metrics to the display
            if metrics_to_show:
                line_parts.append(" | ".join(metrics_to_show))
            
            line_parts.append(f"(ID: {player['id']})")
            result_lines.append(" - ".join(line_parts))
        
        return "\n".join(result_lines)
    except Exception as e:
        # Log the full exception with traceback for debugging
        logging.error(f"Error in search_players: {str(e)}")
        logging.error(f"Exception type: {type(e).__name__}")
        logging.error(f"Traceback: {traceback.format_exc()}")
        
        # Return user-friendly error message
        return f"Error searching players: {str(e)}"



@tool
def get_player_fixtures(players: str, num_fixtures: int = 5) -> str:
    """
    Get fixture difficulty analysis for specific players by mapping them to their teams.

    IMPORTANT: If you need fixtures for many players, send a comma seperated list of their names.
    
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
            team_fixtures = []
            
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