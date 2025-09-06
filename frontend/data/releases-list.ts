export default {
  currentVersion: 3,
  releases: {
    "3": {
      title: "New captain selection algorithm",
      date: "2025-01-09",
      content: `## New Features

- Enhanced captain selection algorithm with weighted scoring system
- Fix player replacement algorithm to prioritise players with easy fixtures 
- New Releases page for tracking updates
- Fix sorting when we want to sort both ascending and descending

## Captain Selection Algorithm

The FPL Agent uses a weighted scoring system to recommend captain options based on five key factors.

### Scoring Formula

| Factor | Weight | Calculation |
|--------|--------|-------------|
| **Total Points** | 40% | \`(player_points / max_points) × 100 × 0.4\` |
| **Form** | 30% | \`(player_form / max_form) × 100 × 0.3\` |
| **Attacking** | 15% | \`(player_xGI / max_xGI) × 100 × 0.15\` |
| **Next Fixture** | 10% | \`(5 - fixture_difficulty) × 25 × 0.1\` |
| **History** | 5% | \`(last_season_ppg / max_ppg) × 100 × 0.05\` |

### Factor Details

- **Total Points**: Season total points, normalized against the current highest player score (highest scorer is 100)
- **Form**: Recent 30 days average, rewards current hot streaks  
- **Attacking**: Expected goal involvements (xG + xA), measures threat
- **Next Fixture**: Inverted difficulty scale (easier = higher score)
- **History**: Previous season PPG, only applied early in the season

### Requirements

Players must be outfield (not GK), £6.0m+, and 60+ minutes played to qualify as captain candidates.
`
    },
    "2": {
      title: "Release 2", 
      date: "2024-12-15",
      content: `## New Features

- Added transfer suggestions based on upcoming fixtures
- Implemented player comparison tool

## Improvements

- Enhanced mobile responsiveness
- Better error handling`
    },
    "1": {
      title: "Release 1",
      date: "2024-11-20", 
      content: `## Initial Release

- Basic FPL agent functionality
- Player search and analysis
- Fixture difficulty assessment
- Simple recommendations

## Features

- Chat-based interface
- Real-time FPL data integration
- User authentication with Clerk
- Responsive design`
    }
  }
};