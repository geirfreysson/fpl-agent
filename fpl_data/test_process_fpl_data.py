#!/usr/bin/env python3
"""
Unit tests for process_fpl_data.py xG form calculation
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
from process_fpl_data import calculate_xg_form_metrics


class TestXGFormCalculation:
    """Test suite for xG form calculation function"""

    def test_xg_form_basic_calculation(self):
        """Test basic calculation with 3 matches in 30 days"""
        # Create test data - 3 matches in last 30 days
        current_date = datetime(2025, 1, 31, 12, 0, 0, tzinfo=timezone.utc)

        test_data = pd.DataFrame({
            'player_id': [1, 1, 1],
            'expected_goals': ['0.5', '0.8', '0.4'],
            'expected_assists': ['0.3', '0.2', '0.5'],
            'expected_goal_involvements': ['0.8', '1.0', '0.9'],
            'kickoff_time': [
                current_date - timedelta(days=5),
                current_date - timedelta(days=15),
                current_date - timedelta(days=25)
            ]
        })

        result = calculate_xg_form_metrics(test_data, current_date)

        # Verify structure
        assert len(result) == 1
        assert result['player_id'].iloc[0] == 1

        # Verify calculations (average of 3 matches)
        expected_xg = (0.5 + 0.8 + 0.4) / 3
        expected_xa = (0.3 + 0.2 + 0.5) / 3
        expected_xgi = (0.8 + 1.0 + 0.9) / 3

        assert result['xg_form_30d'].iloc[0] == pytest.approx(expected_xg, rel=1e-6)
        assert result['xa_form_30d'].iloc[0] == pytest.approx(expected_xa, rel=1e-6)
        assert result['xgi_form_30d'].iloc[0] == pytest.approx(expected_xgi, rel=1e-6)
        assert result['matches_last_30d'].iloc[0] == 3

    def test_xg_form_date_filtering(self):
        """Test that only matches within 30 days are included"""
        current_date = datetime(2025, 1, 31, 12, 0, 0, tzinfo=timezone.utc)

        test_data = pd.DataFrame({
            'player_id': [1, 1, 1, 1],
            'expected_goals': ['0.5', '0.8', '0.4', '0.9'],  # 0.9 should be excluded
            'expected_assists': ['0.3', '0.2', '0.5', '0.6'],  # 0.6 should be excluded
            'expected_goal_involvements': ['0.8', '1.0', '0.9', '1.5'],  # 1.5 should be excluded
            'kickoff_time': [
                current_date - timedelta(days=5),   # Include
                current_date - timedelta(days=15),  # Include
                current_date - timedelta(days=29),  # Include (just within 30 days)
                current_date - timedelta(days=31)   # Exclude (outside 30 days)
            ]
        })

        result = calculate_xg_form_metrics(test_data, current_date)

        # Should only count 3 matches (not 4)
        assert result['matches_last_30d'].iloc[0] == 3

        # Verify calculations exclude the 31-day old match
        expected_xg = (0.5 + 0.8 + 0.4) / 3
        assert result['xg_form_30d'].iloc[0] == pytest.approx(expected_xg, rel=1e-6)

    def test_xg_form_no_recent_matches(self):
        """Test that players with no matches in last 30 days return NaN"""
        current_date = datetime(2025, 1, 31, 12, 0, 0, tzinfo=timezone.utc)

        # All matches are > 30 days old
        test_data = pd.DataFrame({
            'player_id': [1, 1],
            'expected_goals': ['0.5', '0.8'],
            'expected_assists': ['0.3', '0.2'],
            'expected_goal_involvements': ['0.8', '1.0'],
            'kickoff_time': [
                current_date - timedelta(days=45),
                current_date - timedelta(days=50)
            ]
        })

        result = calculate_xg_form_metrics(test_data, current_date)

        # Should return empty DataFrame with correct structure
        assert len(result) == 0
        assert list(result.columns) == ['player_id', 'xg_form_30d', 'xa_form_30d',
                                        'xgi_form_30d', 'matches_last_30d']

    def test_xg_form_type_conversion(self):
        """Test conversion of string xG values to float64"""
        current_date = datetime(2025, 1, 31, 12, 0, 0, tzinfo=timezone.utc)

        # Mix of valid strings and invalid values
        test_data = pd.DataFrame({
            'player_id': [1, 1, 2],
            'expected_goals': ['0.5', '0.8', 'invalid'],
            'expected_assists': ['0.3', '0.2', '0.4'],
            'expected_goal_involvements': ['0.8', '1.0', '0.9'],
            'kickoff_time': [
                current_date - timedelta(days=5),
                current_date - timedelta(days=15),
                current_date - timedelta(days=10)
            ]
        })

        result = calculate_xg_form_metrics(test_data, current_date)

        # Player 1 should have valid averages
        player_1 = result[result['player_id'] == 1].iloc[0]
        assert player_1['xg_form_30d'] == pytest.approx(0.65, rel=1e-6)

        # Player 2 should have NaN for xG due to invalid conversion
        player_2 = result[result['player_id'] == 2].iloc[0]
        assert pd.isna(player_2['xg_form_30d'])

    def test_xg_form_edge_cases(self):
        """Test edge cases: 1 match, 2 matches (should return average)"""
        current_date = datetime(2025, 1, 31, 12, 0, 0, tzinfo=timezone.utc)

        # Player 1: Only 1 match
        # Player 2: 2 matches
        test_data = pd.DataFrame({
            'player_id': [1, 2, 2],
            'expected_goals': ['0.5', '0.8', '0.4'],
            'expected_assists': ['0.3', '0.2', '0.6'],
            'expected_goal_involvements': ['0.8', '1.0', '1.0'],
            'kickoff_time': [
                current_date - timedelta(days=5),
                current_date - timedelta(days=10),
                current_date - timedelta(days=20)
            ]
        })

        result = calculate_xg_form_metrics(test_data, current_date)

        # Player 1: 1 match - should return that value
        player_1 = result[result['player_id'] == 1].iloc[0]
        assert player_1['xg_form_30d'] == pytest.approx(0.5, rel=1e-6)
        assert player_1['matches_last_30d'] == 1

        # Player 2: 2 matches - should return average
        player_2 = result[result['player_id'] == 2].iloc[0]
        assert player_2['xg_form_30d'] == pytest.approx(0.6, rel=1e-6)
        assert player_2['matches_last_30d'] == 2

    def test_xg_form_timezone_handling(self):
        """Test timezone-aware datetime comparison"""
        # Use explicit UTC timezone
        current_date = datetime(2025, 1, 31, 12, 0, 0, tzinfo=timezone.utc)

        # Create timestamps in UTC
        test_data = pd.DataFrame({
            'player_id': [1, 1],
            'expected_goals': ['0.5', '0.8'],
            'expected_assists': ['0.3', '0.2'],
            'expected_goal_involvements': ['0.8', '1.0'],
            'kickoff_time': [
                '2025-01-26T15:00:00Z',  # 5 days ago
                '2025-01-16T15:00:00Z'   # 15 days ago
            ]
        })

        result = calculate_xg_form_metrics(test_data, current_date)

        # Should successfully parse and compare timezone-aware datetimes
        assert len(result) == 1
        assert result['matches_last_30d'].iloc[0] == 2
        assert result['xg_form_30d'].iloc[0] == pytest.approx(0.65, rel=1e-6)

    def test_xg_form_multiple_players(self):
        """Test calculation with multiple players"""
        current_date = datetime(2025, 1, 31, 12, 0, 0, tzinfo=timezone.utc)

        test_data = pd.DataFrame({
            'player_id': [1, 1, 2, 2, 2],
            'expected_goals': ['0.5', '0.8', '0.3', '0.4', '0.2'],
            'expected_assists': ['0.3', '0.2', '0.5', '0.6', '0.4'],
            'expected_goal_involvements': ['0.8', '1.0', '0.8', '1.0', '0.6'],
            'kickoff_time': [
                current_date - timedelta(days=5),
                current_date - timedelta(days=15),
                current_date - timedelta(days=8),
                current_date - timedelta(days=18),
                current_date - timedelta(days=28)
            ]
        })

        result = calculate_xg_form_metrics(test_data, current_date)

        # Should have 2 players
        assert len(result) == 2

        # Verify player 1
        player_1 = result[result['player_id'] == 1].iloc[0]
        assert player_1['matches_last_30d'] == 2
        assert player_1['xg_form_30d'] == pytest.approx(0.65, rel=1e-6)

        # Verify player 2
        player_2 = result[result['player_id'] == 2].iloc[0]
        assert player_2['matches_last_30d'] == 3
        assert player_2['xg_form_30d'] == pytest.approx(0.3, rel=1e-6)
