# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running python files and tests

To run a python file, use the following command:
```bash
uv run python <file_name>.py
```

To run a test, use the following command:
```bash
uv run pytest <test_file_name>.py
```

## Project Overview

This is a full-stack Fantasy Premier League (FPL) AI assistant application. It consists of:

- **Frontend**: Next.js 15 application with React 19, TypeScript, and Tailwind CSS
- **Backend**: Python backend with specialized FPL analysis tools
- **Data Processing**: Automated FPL data pipeline from official API
- **Architecture**: Frontend serves as a proxy to the Python backend via `/api/chat` route

## Development Commands

### Frontend (Next.js)
```bash
cd frontend
npm run dev          # Start development server with Turbopack
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
```

### Backend (Python)
```bash
cd backend
python main.py       # Start FastAPI server on port 8000
pytest tests/        # Run backend tests
```

### Environment Setup
Create `frontend/.env.local` with:
```
# Clerk Authentication
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...

# Backend URL
BACKEND_URL=http://localhost:8000  # Optional, defaults to localhost:8000
```

For the backend, set the environment variables:
```bash
export OPENAI_API_KEY=sk-your-key-here
export CLERK_SECRET_KEY=sk_test_...       # Backend key for API verification
```

## Architecture

### Frontend Structure
- `app/page.tsx` - Main entry point, renders Assistant component
- `app/assistant.tsx` - Main assistant interface using assistant-ui
- `app/api/chat/route.ts` - API proxy that forwards requests to Python backend
- `components/assistant-ui/` - Custom assistant-ui components
- `components/ui/` - Reusable UI components using Radix UI primitives

### Backend Structure
- `main.py` - Entry point, starts uvicorn server on port 8000
- `api.py` - FastAPI application with CORS middleware and `/api/chat` endpoint
- `agents.py` - Creates ToolCallingAgent using smolagents library
- `tools.py` - Comprehensive FPL analysis tools with 28+ enhanced features
- `tests/` - Backend test suite

### FPL Data Structure
- `fpl_data/` - Directory containing processed FPL data files
- `fpl_data/process_fpl_data.py` - Data processing script that fetches and normalizes FPL data
- `fpl_data/DATA_STRUCTURE.md` - Comprehensive documentation of all data files and schemas

### Backend Integration
- Frontend makes POST requests to `/api/chat`
- Route handler forwards messages to Python backend at `$BACKEND_URL/api/chat`
- Backend uses smolagents ToolCallingAgent with LiteLLM model (gpt-4o-mini)
- Returns streaming responses in assistant-ui compatible format
- Conversation history is maintained and passed to backend

### Key Dependencies

#### Frontend
- `@assistant-ui/react` - Core assistant UI framework
- `@ai-sdk/openai` - OpenAI integration
- `@radix-ui/*` - UI primitives
- `tailwindcss` - Styling framework
- `lucide-react` - Icons

#### Backend
- `fastapi` - Modern Python web framework
- `smolagents` - AI agent framework with tool calling capabilities
- `litellm` - Unified LLM API interface
- `uvicorn` - ASGI server for FastAPI
- `httpx` - HTTP client for async requests

## Development Notes

### Backend Implementation
- Backend uses smolagents ToolCallingAgent with specialized FPL analysis tools
- Includes comprehensive FPL data analysis capabilities with 28+ enhanced features
- Agent responses are streamed using FastAPI's StreamingResponse
- CORS is configured to allow requests from frontend (localhost:3000)
- Request/response format is compatible with assistant-ui expectations

### FPL Data Analysis Features
- **Player Search**: Advanced filtering with 50+ parameters including enhanced metrics
- **Performance Analysis**: Expected vs actual performance metrics, consistency analysis
- **Value Analysis**: Points per million, form per million, efficiency metrics
- **Fixture Difficulty**: Forward-looking analysis (3, 5, 10 gameweek horizons)
- **Position-Specific**: Tailored metrics for GK, DEF, MID, FWD positions
- **Transfer Trends**: Ownership categories, transfer momentum analysis
- **Ranking Systems**: Position-based rankings for points, value, and form

### Integration Flow
1. Frontend sends user messages via `/api/chat` route
2. Next.js API route forwards to Python backend at `/api/chat`
3. Backend creates agent instance and processes FPL-related queries
4. Agent can call specialized FPL tools for data analysis, player searches, etc.
5. Response is streamed back through the frontend proxy
6. Frontend renders streaming response in assistant-ui interface

### Adding New Tools
To extend the backend with new capabilities:
1. Define new tool functions in `tools.py` using `@tool` decorator
2. Import and add to tools list in `agents.py`
3. Agent will automatically have access to new tools

### FPL Data Files Structure
The application uses 5 main data files (updated automatically by `process_fpl_data.py`):

1. **`elements.parquet`** (663 players, 97+ columns):
   - Player basic info, current season stats, enhanced derived features
   - Value metrics: points_per_million, form_per_million, points_per_minute
   - Performance analysis: goals_overperformance, assists_overperformance, luck_factors
   - Fixture difficulty: avg_fixture_difficulty_3/5/10, home/away splits
   - Position rankings: points_rank_in_position, value_rank_in_position

2. **`fixtures.parquet`** (380 fixtures, 17 columns):
   - Match fixtures, kickoff times, difficulty ratings, scores

3. **`player_fixtures.parquet`** (1,900 records, 15 columns):
   - Player-specific fixture data with home/away flags, difficulty ratings

4. **`player_history_past.parquet`** (239 records, 29 columns):
   - Historical season performance data for trend analysis

5. **`teams.json`** (20 teams):
   - Team info, strength ratings, league positions

### Key Data Relationships
- `elements.id` ↔ `player_fixtures.player_id` ↔ `player_history_past.player_id`
- `elements.team` ↔ `teams[].id` (team lookup)
- `fixtures.team_h/team_a` ↔ `teams[].id` (team lookup)

- Frontend expects backend to be running on port 8000
- All API communication flows through the Next.js API route for proper CORS handling
- Error handling includes fallback error streams for assistant-ui compatibility

## Installing packages
The project uses uv as a package manager. To install packages, run:
```bash
uv add <package_name>
```

