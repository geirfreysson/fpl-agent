# FPL Backend Test Suite

This directory contains comprehensive tests for the FPL backend tools and functionality.

## Test Structure

### Test Files

- **`test_search_players.py`** - Tests for the main `search_players` function
  - Limit functionality
  - Position filtering
  - Sorting (including fallback logic)
  - Price filtering
  - Team filtering
  - Dual sorting
  - Error handling

- **`test_fpl_tools.py`** - Tests for other FPL analysis tools
  - `get_players_by_price_range`
  - `get_player_fixtures`
  - `get_player_form`
  - `find_player_replacements`
  - `get_easiest_fixtures`
  - `help` function

- **`test_integration.py`** - Integration tests
  - Multi-step workflows
  - Data consistency across functions
  - Complex filter combinations
  - Large dataset handling

### Configuration Files

- **`conftest.py`** - Pytest configuration and shared fixtures
- **`pytest.ini`** - Pytest settings and markers
- **`run_tests.py`** - Custom test runner with options

## Running Tests

### Quick Start

```bash
# Run all tests
uv run python run_tests.py

# Or use pytest directly
uv run pytest tests/
```

### Test Options

```bash
# Run only fast tests (exclude slow/integration)
uv run python run_tests.py --fast

# Run only unit tests
uv run python run_tests.py --unit

# Run only integration tests  
uv run python run_tests.py --integration

# Run specific test file
uv run python run_tests.py test_search_players.py

# Get help
uv run python run_tests.py --help
```

### Pytest Direct Usage

```bash
# Run with verbose output
uv run pytest tests/ -v

# Run specific test class
uv run pytest tests/test_search_players.py::TestSearchPlayers -v

# Run specific test method
uv run pytest tests/test_search_players.py::TestSearchPlayers::test_basic_limit_functionality -v

# Run tests matching pattern
uv run pytest tests/ -k "limit" -v

# Run with coverage (if coverage installed)
uv run pytest tests/ --cov=tools --cov-report=html
```

## Test Categories

### Unit Tests (marked with `@pytest.mark.unit`)
- Test individual functions in isolation
- Fast execution
- Mock external dependencies where needed

### Integration Tests (marked with `@pytest.mark.integration`) 
- Test multiple functions working together
- Real data interactions
- End-to-end workflows

### Slow Tests (marked with `@pytest.mark.slow`)
- Tests that take longer to run
- Large dataset operations
- Complex filter combinations

## Key Test Scenarios

### Search Players Function
- ✅ Limit parameter works correctly (returns exact number requested)
- ✅ Position filtering (GK, DEF, MID, FWD)
- ✅ Sorting by various columns (total_points, form, threat, etc.)
- ✅ Fallback logic (attacking_threat → threat)
- ✅ Price range filtering
- ✅ Team filtering
- ✅ Dual sorting functionality
- ✅ Error handling for invalid inputs

### Other Tools
- ✅ Price range queries work correctly
- ✅ Player fixture analysis
- ✅ Form analysis (single and multiple players)
- ✅ Player replacement suggestions
- ✅ Easiest fixtures analysis
- ✅ Help function returns useful information

### Integration
- ✅ Search → Fixtures workflow
- ✅ Search → Form analysis workflow
- ✅ Complex multi-filter queries
- ✅ Data consistency across functions
- ✅ Large limit handling

## Adding New Tests

1. **Unit Tests**: Add to appropriate `test_*.py` file
2. **Integration Tests**: Add to `test_integration.py`
3. **New Tool**: Create new test file `test_your_tool.py`

### Test Naming Convention
- Test files: `test_*.py`
- Test classes: `TestYourTool`
- Test methods: `test_specific_functionality`

### Example Test

```python
def test_your_functionality(self):
    """Test description"""
    result = your_function(param1="value", param2=10)
    
    assert "expected content" in result
    assert len(result) > 50
    # Add specific assertions
```

## Fixtures Available

- `sample_player_names` - Common player names for testing
- `sample_team_names` - Team names for testing
- `test_positions` - Valid position names
- `test_price_ranges` - Common price ranges

## Continuous Integration

These tests are designed to:
- Run quickly in CI environments
- Catch regressions in functionality
- Validate data processing logic
- Ensure API consistency

## Troubleshooting

### Common Issues

1. **Data file not found**: Ensure you're running from the backend directory
2. **Import errors**: Check that backend is in Python path (handled by conftest.py)
3. **Slow tests**: Use `--fast` option to skip integration tests

### Debug Mode

```bash
# Run with Python debugger on failure
uv run pytest tests/ --pdb

# Stop on first failure
uv run pytest tests/ -x

# Show local variables in tracebacks
uv run pytest tests/ -l
```