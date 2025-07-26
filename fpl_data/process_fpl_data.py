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


def process_fpl_data():
    """
    Process both elements and fixtures data.
    """
    print("=== Processing FPL Data ===")
    
    # Process elements data
    print("\n1. Processing elements data...")
    process_elements_data()
    
    # Process fixtures data
    print("\n2. Processing fixtures data...")
    process_fixtures_data()
    
    print("\n=== All data processing complete! ===")


if __name__ == "__main__":
    try:
        process_fpl_data()
    except Exception as e:
        print(f"Error: {e}")
        exit(1)