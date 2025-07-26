#!/usr/bin/env python3
"""
FPL Data Processor

This script reads the bootstrap_static.json file, extracts the 'elements' data,
and saves it to a parquet file for efficient storage and analysis.
"""

import json
import pandas as pd
from pathlib import Path


def process_elements_data():
    """
    Read bootstrap_static.json, extract elements data, and save to parquet.
    """
    # Define file paths
    input_file = Path("fpl_data/bootstrap_static.json")
    output_file = Path("fpl_data/elements.parquet")
    
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
    print(f"Found {len(elements_data)} elements in the data")
    
    # Convert to DataFrame
    df = pd.DataFrame(elements_data)
    
    # Create output directory if it doesn't exist
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Save to parquet
    print(f"Saving elements data to {output_file}...")
    df.to_parquet(output_file, index=False)
    
    print(f"Successfully saved {len(df)} elements records to {output_file}")
    print(f"Elements DataFrame shape: {df.shape}")
    print(f"Elements columns: {list(df.columns)[:10]}...")  # Show first 10 columns


def process_fixtures_data():
    """
    Read fixtures.json and save to parquet.
    """
    # Define file paths
    input_file = Path("fpl_data/fixtures.json")
    output_file = Path("fpl_data/fixtures.parquet")
    
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
    input_file = Path("fpl_data/bootstrap_static.json")
    output_file = Path("fpl_data/teams.json")
    
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
    input_file = Path("fpl_data/player_summaries.json")
    
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
            fixtures_output = Path("fpl_data/player_fixtures.parquet")
            fixtures_df.to_parquet(fixtures_output, index=False)
            print(f"Saved player fixtures: {len(fixtures_df)} records, {len(fixtures_df.columns)} columns")
            print(f"Columns: {list(fixtures_df.columns)}")
        else:
            print("No player fixtures data found")
        
        # Player current season history
        if all_history:
            history_df = pd.DataFrame(all_history)
            history_output = Path("fpl_data/player_history.parquet")
            history_df.to_parquet(history_output, index=False)
            print(f"Saved player history: {len(history_df)} records, {len(history_df.columns)} columns")
            print(f"Columns: {list(history_df.columns)}")
        else:
            print("No player current season history data found (expected if season hasn't started)")
        
        # Player historical seasons
        if all_history_past:
            history_past_df = pd.DataFrame(all_history_past)
            history_past_output = Path("fpl_data/player_history_past.parquet")
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