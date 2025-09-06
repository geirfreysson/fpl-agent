# Captain Selection Algorithm

The FPL Agent uses a weighted scoring system to recommend captain options based on five key factors.

## Scoring Formula

| Factor | Weight | Calculation |
|--------|--------|-------------|
| **Total Points** | 40% | `(player_points / max_points) × 100 × 0.4` |
| **Form** | 30% | `(player_form / max_form) × 100 × 0.3` |
| **Attacking** | 15% | `(player_xGI / max_xGI) × 100 × 0.15` |
| **Next Fixture** | 10% | `(5 - fixture_difficulty) × 25 × 0.1` |
| **History** | 5% | `(last_season_ppg / max_ppg) × 100 × 0.05` |

## Factor Details

- **Total Points**: Season total points, normalized against pool maximum
- **Form**: Recent 5-gameweek average, rewards current hot streaks  
- **Attacking**: Expected goal involvements (xG + xA), measures threat
- **Next Fixture**: Inverted difficulty scale (easier = higher score)
- **History**: Previous season PPG, early season only

## Requirements

Players must be outfield (not GK), £6.0m+, and 60+ minutes played to qualify as captain candidates.