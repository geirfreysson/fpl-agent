#!/usr/bin/env python3
"""
FPL Data Processor

This script reads the bootstrap_static.json file, extracts the 'elements' data,
and saves it to a parquet file for efficient storage and analysis.
Now includes comprehensive feature engineering for FPL analysis.
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path


def calculate_fixture_difficulty(team_id, fixtures_df, teams_lookup, num_fixtures=5):
    """
    Calculate average fixture difficulty for a team's next N fixtures.
    """
    try:
        # Get upcoming fixtures for this team
        upcoming_fixtures = fixtures_df[fixtures_df['finished'] == False].sort_values('event')
        
        # Home fixtures
        home_fixtures = upcoming_fixtures[upcoming_fixtures['team_h'] == team_id][['team_a', 'team_h_difficulty', 'event']].copy()
        if not home_fixtures.empty:
            home_fixtures['difficulty'] = home_fixtures['team_h_difficulty']
            home_fixtures['venue'] = 'H'
        
        # Away fixtures
        away_fixtures = upcoming_fixtures[upcoming_fixtures['team_a'] == team_id][['team_h', 'team_a_difficulty', 'event']].copy()
        if not away_fixtures.empty:
            away_fixtures['difficulty'] = away_fixtures['team_a_difficulty']
            away_fixtures['venue'] = 'A'
        
        # Combine and sort by event
        all_fixtures = pd.concat([
            home_fixtures[['difficulty', 'event', 'venue']] if not home_fixtures.empty else pd.DataFrame(),
            away_fixtures[['difficulty', 'event', 'venue']] if not away_fixtures.empty else pd.DataFrame()
        ]).sort_values('event').head(num_fixtures)
        
        if all_fixtures.empty:
            return None, None, None
        
        avg_difficulty = all_fixtures['difficulty'].mean()
        home_difficulty = all_fixtures[all_fixtures['venue'] == 'H']['difficulty'].mean() if 'H' in all_fixtures['venue'].values else None
        away_difficulty = all_fixtures[all_fixtures['venue'] == 'A']['difficulty'].mean() if 'A' in all_fixtures['venue'].values else None
        
        return avg_difficulty, home_difficulty, away_difficulty
    except Exception:
        return None, None, None


def add_derived_features(df, fixtures_df=None, teams_data=None):
    """
    Add comprehensive derived features for FPL analysis.
    """
    print("Adding derived features...")
    
    # Convert numeric columns
    numeric_cols = ['now_cost', 'total_points', 'form', 'points_per_game', 'minutes', 
                   'goals_scored', 'assists', 'expected_goals', 'expected_assists',
                   'expected_goal_involvements', 'clean_sheets', 'goals_conceded',
                   'saves', 'bonus', 'bps', 'influence', 'creativity', 'threat',
                   'ict_index', 'selected_by_percent', 'transfers_in', 'transfers_out']
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Price in millions
    df['price_millions'] = df['now_cost'] / 10
    
    # === VALUE METRICS ===
    df['points_per_million'] = np.where(df['price_millions'] > 0, df['total_points'] / df['price_millions'], 0)
    df['form_per_million'] = np.where(df['price_millions'] > 0, df['form'] / df['price_millions'], 0)
    df['expected_goals_per_million'] = np.where(df['price_millions'] > 0, df['expected_goals'] / df['price_millions'], 0)
    
    # === PERFORMANCE EFFICIENCY ===
    df['minutes_per_game'] = np.where(df['starts'] > 0, df['minutes'] / df['starts'], 0)
    df['points_per_minute'] = np.where(df['minutes'] > 0, df['total_points'] / df['minutes'], 0)
    df['goal_involvement_rate'] = (df['goals_scored'] + df['assists']) / np.maximum(df['minutes'] / 90, 1)
    
    # === EXPECTED VS ACTUAL PERFORMANCE ===
    df['goals_overperformance'] = df['goals_scored'] - df['expected_goals']
    df['assists_overperformance'] = df['assists'] - df['expected_assists']
    df['total_overperformance'] = df['goals_overperformance'] + df['assists_overperformance']
    
    # Luck factor (ratio of actual to expected)
    df['goals_luck_factor'] = np.where(df['expected_goals'] > 0, df['goals_scored'] / df['expected_goals'], 1)
    df['assists_luck_factor'] = np.where(df['expected_assists'] > 0, df['assists'] / df['expected_assists'], 1)
    
    # === CONSISTENCY METRICS ===
    # Form consistency (based on form vs points_per_game)
    df['form_consistency'] = np.where(df['points_per_game'] > 0, 
                                    1 - abs(df['form'] - df['points_per_game']) / df['points_per_game'], 0)
    
    # === OWNERSHIP AND TRANSFER METRICS ===
    df['transfer_momentum'] = df['transfers_in'] - df['transfers_out']
    df['ownership_category'] = pd.cut(df['selected_by_percent'], 
                                    bins=[0, 5, 15, 30, 100], 
                                    labels=['Low', 'Medium', 'High', 'Template'])
    
    # === POSITION-SPECIFIC FEATURES ===
    position_map = {1: 'GK', 2: 'DEF', 3: 'MID', 4: 'FWD'}
    df['position'] = df['element_type'].map(position_map)
    
    # Goalkeeper specific
    gk_mask = df['element_type'] == 1
    df.loc[gk_mask, 'save_percentage'] = np.where(
        (df.loc[gk_mask, 'saves'] + df.loc[gk_mask, 'goals_conceded']) > 0,
        df.loc[gk_mask, 'saves'] / (df.loc[gk_mask, 'saves'] + df.loc[gk_mask, 'goals_conceded']),
        0
    )
    df.loc[gk_mask, 'clean_sheet_rate'] = np.where(
        df.loc[gk_mask, 'starts'] > 0,
        df.loc[gk_mask, 'clean_sheets'] / df.loc[gk_mask, 'starts'],
        0
    )
    
    # Defender specific
    def_mask = df['element_type'] == 2
    df.loc[def_mask, 'defensive_value'] = (df.loc[def_mask, 'clean_sheets'] * 4 + 
                                         df.loc[def_mask, 'goals_scored'] * 6 + 
                                         df.loc[def_mask, 'assists'] * 3)
    
    # Midfielder/Forward attacking threat
    att_mask = df['element_type'].isin([3, 4])
    df.loc[att_mask, 'attacking_threat'] = (df.loc[att_mask, 'goals_scored'] + 
                                          df.loc[att_mask, 'assists'] + 
                                          df.loc[att_mask, 'expected_goal_involvements'])
    
    # === FIXTURE DIFFICULTY (if fixtures data available) ===
    if fixtures_df is not None and teams_data is not None:
        print("Calculating fixture difficulties...")
        teams_lookup = {team['id']: team['name'] for team in teams_data}
        
        # Initialize fixture difficulty columns
        df['avg_fixture_difficulty_3'] = None
        df['avg_fixture_difficulty_5'] = None
        df['avg_fixture_difficulty_10'] = None
        df['home_fixture_difficulty_5'] = None
        df['away_fixture_difficulty_5'] = None
        
        # Calculate for each team
        for team_id in df['team'].unique():
            if pd.isna(team_id):
                continue
            
            team_id = int(team_id)
            team_mask = df['team'] == team_id
            
            # Calculate different fixture windows
            avg_3, _, _ = calculate_fixture_difficulty(team_id, fixtures_df, teams_lookup, 3)
            avg_5, home_5, away_5 = calculate_fixture_difficulty(team_id, fixtures_df, teams_lookup, 5)
            avg_10, _, _ = calculate_fixture_difficulty(team_id, fixtures_df, teams_lookup, 10)
            
            df.loc[team_mask, 'avg_fixture_difficulty_3'] = avg_3
            df.loc[team_mask, 'avg_fixture_difficulty_5'] = avg_5
            df.loc[team_mask, 'avg_fixture_difficulty_10'] = avg_10
            df.loc[team_mask, 'home_fixture_difficulty_5'] = home_5
            df.loc[team_mask, 'away_fixture_difficulty_5'] = away_5
    
    # === RANKING WITHIN POSITION ===
    for pos in [1, 2, 3, 4]:
        pos_mask = df['element_type'] == pos
        if pos_mask.any():
            df.loc[pos_mask, 'points_rank_in_position'] = df.loc[pos_mask, 'total_points'].rank(ascending=False)
            df.loc[pos_mask, 'value_rank_in_position'] = df.loc[pos_mask, 'points_per_million'].rank(ascending=False)
            df.loc[pos_mask, 'form_rank_in_position'] = df.loc[pos_mask, 'form'].rank(ascending=False)
    
    print(f"Added {len([col for col in df.columns if col not in numeric_cols + ['id', 'web_name', 'first_name', 'second_name']])} derived features")
    return df


def process_elements_data():
    """
    Read bootstrap_static.json, extract elements data, add derived features, and save to parquet.
    """
    # Define file paths
    input_file = Path("fpl_data/fpl_data/bootstrap_static.json")
    output_file = Path("fpl_data/fpl_data/elements.parquet")
    fixtures_file = Path("fpl_data/fpl_data/fixtures.parquet")
    
    # Check if input file exists
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    print(f"Reading elements data from {input_file}...")
    
    # Read the JSON file
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract the elements data
    if 'elements' not in data:
        raise KeyError("'elements' key not found in the JSON data")
    
    elements_data = data['elements']
    teams_data = data.get('teams', [])
    print(f"Found {len(elements_data)} elements in the data")
    
    # Convert to DataFrame
    df = pd.DataFrame(elements_data)
    
    # Load fixtures data if available for fixture difficulty calculation
    fixtures_df = None
    if fixtures_file.exists():
        print("Loading fixtures data for difficulty calculation...")
        fixtures_df = pd.read_parquet(fixtures_file)
    
    # Add derived features
    df = add_derived_features(df, fixtures_df, teams_data)
    
    # Create output directory if it doesn't exist
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Save to parquet
    print(f"Saving enhanced elements data to {output_file}...")
    df.to_parquet(output_file, index=False)
    
    print(f"Successfully saved {len(df)} elements records to {output_file}")
    print(f"Elements DataFrame shape: {df.shape}")
    print(f"Total columns: {len(df.columns)}")
    
    # Show sample of new features
    new_features = ['price_millions', 'points_per_million', 'form_per_million', 'goals_overperformance', 
                   'transfer_momentum', 'avg_fixture_difficulty_5', 'points_rank_in_position']
    available_features = [f for f in new_features if f in df.columns]
    if available_features:
        print(f"\nSample of new features: {available_features}")
        print(df[['web_name', 'position'] + available_features].head(3).to_string())


def process_fixtures_data():
    """
    Read fixtures.json and save to parquet.
    """
    # Define file paths
    input_file = Path("fpl_data/fpl_data/fixtures.json")
    output_file = Path("fpl_data/fpl_data/fixtures.parquet")
    
    # Check if input file exists
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    print(f"Reading fixtures data from {input_file}...")
    
    # Read the JSON file
    with open(input_file, 'r', encoding='utf-8') as f:
        fixtures_data = json.load(f)
    
    # Validate that it's a list
    if not isinstance(fixtures_data, list):
        raise ValueError("Expected fixtures.json to contain a JSON array")
    
    print(f"Found {len(fixtures_data)} fixtures in the data")
    
    # Convert to DataFrame
    df = pd.DataFrame(fixtures_data)
    
    # Create output directory if it doesn't exist
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Save to parquet
    print(f"Saving fixtures data to {output_file}...")
    df.to_parquet(output_file, index=False)
    
    print(f"Successfully saved {len(df)} fixtures records to {output_file}")
    print(f"Fixtures DataFrame shape: {df.shape}")
    print(f"Fixtures columns: {list(df.columns)}")


def process_teams_data():
    """
    Extract teams data from bootstrap_static.json and save as teams.json.
    """
    input_file = Path("fpl_data/fpl_data/bootstrap_static.json")
    output_file = Path("fpl_data/fpl_data/teams.json")
    
    try:
        # Read the bootstrap_static JSON file
        with open(input_file, 'r', encoding='utf-8') as f:
            bootstrap_data = json.load(f)
        
        # Extract teams data
        teams_data = bootstrap_data.get('teams', [])
        
        if teams_data:
            # Save teams data as JSON
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(teams_data, f, indent=2, ensure_ascii=False)
            
            print(f"Saved teams data: {len(teams_data)} teams to {output_file}")
            
            # Show sample team data
            if teams_data:
                sample_team = teams_data[0]
                print(f"Sample team keys: {list(sample_team.keys())}")
        else:
            print("No teams data found in bootstrap_static.json")
        
    except FileNotFoundError:
        print(f"Error: {input_file} not found")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    except Exception as e:
        print(f"Error processing teams data: {e}")


def process_player_summaries():
    """
    Read player_summaries.json and split into normalized parquet files.
    """
    # Define file paths
    input_file = Path("fpl_data/fpl_data/player_summaries.json")
    
    try:
        # Read the player summaries JSON file
        with open(input_file, 'r', encoding='utf-8') as f:
            player_summaries = json.load(f)
        
        print(f"Loaded player summaries for {len(player_summaries)} players")
        
        # Initialize lists to collect data
        all_fixtures = []
        all_history = []
        all_history_past = []
        
        # Process each player's data
        for player_id, player_data in player_summaries.items():
            player_id_int = int(player_id)
            
            # Process fixtures
            for fixture in player_data.get('fixtures', []):
                fixture_with_id = fixture.copy()
                fixture_with_id['player_id'] = player_id_int
                all_fixtures.append(fixture_with_id)
            
            # Process current season history
            for history in player_data.get('history', []):
                history_with_id = history.copy()
                history_with_id['player_id'] = player_id_int
                all_history.append(history_with_id)
            
            # Process historical seasons
            for history_past in player_data.get('history_past', []):
                history_past_with_id = history_past.copy()
                history_past_with_id['player_id'] = player_id_int
                all_history_past.append(history_past_with_id)
        
        # Create DataFrames and save as parquet files
        
        # Player fixtures
        if all_fixtures:
            fixtures_df = pd.DataFrame(all_fixtures)
            fixtures_output = Path("fpl_data/fpl_data/player_fixtures.parquet")
            fixtures_df.to_parquet(fixtures_output, index=False)
            print(f"Saved player fixtures: {len(fixtures_df)} records, {len(fixtures_df.columns)} columns")
            print(f"Columns: {list(fixtures_df.columns)}")
        else:
            print("No player fixtures data found")
        
        # Player current season history
        if all_history:
            history_df = pd.DataFrame(all_history)
            history_output = Path("fpl_data/fpl_data/player_history.parquet")
            history_df.to_parquet(history_output, index=False)
            print(f"Saved player history: {len(history_df)} records, {len(history_df.columns)} columns")
            print(f"Columns: {list(history_df.columns)}")
        else:
            print("No player current season history data found (expected if season hasn't started)")
        
        # Player historical seasons
        if all_history_past:
            history_past_df = pd.DataFrame(all_history_past)
            history_past_output = Path("fpl_data/fpl_data/player_history_past.parquet")
            history_past_df.to_parquet(history_past_output, index=False)
            print(f"Saved player history past: {len(history_past_df)} records, {len(history_past_df.columns)} columns")
            print(f"Columns: {list(history_past_df.columns)}")
        else:
            print("No player historical data found")
        
    except FileNotFoundError:
        print(f"Error: {input_file} not found")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    except Exception as e:
        print(f"Error processing player summaries: {e}")


def process_fpl_data():
    """
    Process elements, fixtures, player summaries, and teams data.
    """
    print("=== Processing FPL Data ===")
    
    # Process elements data
    print("\n1. Processing elements data...")
    process_elements_data()
    
    # Process fixtures data
    print("\n2. Processing fixtures data...")
    process_fixtures_data()
    
    # Process player summaries data
    print("\n3. Processing player summaries data...")
    process_player_summaries()
    
    # Process teams data
    print("\n4. Processing teams data...")
    process_teams_data()
    
    print("\n=== All data processing complete! ===")


if __name__ == "__main__":
    try:
        process_fpl_data()
    except Exception as e:
        print(f"Error: {e}")
        exit(1)