export default {
  currentVersion: 6,
  releases: {
    "6": {
      title: "XG Form Analysis - 30-Day Rolling Metrics",
      date: "2026-01-31",
      content: `## New Features

- **30-Day xG Form Metrics**: Track player performance using rolling 30-day averages for expected goals (xG), expected assists (xA), and expected goal involvements (xGI)
- **Expanded Player Coverage**: Increased detailed player data from 50 to 150 top players
- **Smart Filtering**: New filter parameters for xG form analysis with match count context

## XG Form Metrics

The agent now calculates rolling 30-day averages based on actual match dates (not gameweeks), providing more accurate short-term form indicators:

- **xG Form**: Average expected goals per match over the last 30 days - identifies players in good underlying form
- **xA Form**: Average expected assists per match over the last 30 days - indicates creative output potential
- **xGI Form**: Average expected goal involvements per match over the last 30 days - best overall attacking threat indicator
- **Matches Last 30 Days**: Number of matches played for context and filtering

## Example Queries

> Show me players with highest xGI form over the last 30 days

> Find midfielders with xG form > 0.5 but low actual goals (due for returns)

> Which forwards have the best xG form with at least 4 matches played?

> Compare players' xG form to their season xG totals
`
    },
    "5": {
      title: "Team fixtures",
      date: "2024-10-20", 
      content: `## New Features

- Team fixtures tool to accurately get upcoming fixtures for any team or list all of them.


### Example prompt:

> Show me the difficulty rating for all the teams for the next 5 games. List them in order, easiest to hardest.
`
    },
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
