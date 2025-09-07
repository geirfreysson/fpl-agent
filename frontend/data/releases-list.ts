export default {
  currentVersion: 4,
  releases: {
    "4": {
      title: "Buttons to share your research",
      date: "2024-09-07", 
      content: `## New Features

- Share all tables on X/Twitter
- Download image of table
- Copy image of table

## Share research
All tables now have Share, Download, and Copy options under all tables.
`
    },



    "3": {
      title: "New captain selection algorithm",
      date: "2025-09-01",
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
      title: "Add fixture information to replacement suggestion", 
      date: "2025-08-15",
      content: `## New Features

- Added transfer suggestions based on upcoming fixtures
- Implemented player comparison tool

## Improvements

- Enhanced mobile responsiveness
- Better error handling`
    },
    "1": {
      title: "Launch FPL With Robots",
      date: "2024-07-27", 
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