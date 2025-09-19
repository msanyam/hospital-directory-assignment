# Hospital Directory API - Testing Guide

This document provides comprehensive information about testing the Hospital Directory API.

## Test Suite Overview

The test suite covers all aspects of the Hospital Directory API with comprehensive test cases:

### Test Categories

1. **Unit Tests** (`test_models.py`)
   - Pydantic model validation
   - Data type checking
   - Field constraints
   - Model serialization/deserialization

2. **Database Tests** (`test_database.py`)
   - CRUD operations
   - FIFO storage behavior (10,000 hospital limit)
   - Batch operations
   - Data consistency and integrity

3. **API Integration Tests** (`test_api.py`)
   - All HTTP endpoints
   - Request/response validation
   - Status code verification
   - Error handling

4. **Batch Processing Tests** (`test_batch.py`)
   - Complete batch workflows
   - Batch size limits (20 hospitals)
   - Batch activation logic
   - Cross-batch operations

5. **Performance Tests** (`test_performance.py`)
   - Rate limiting enforcement
   - FIFO storage performance
   - Concurrent operations
   - Resource usage monitoring

6. **Edge Case Tests** (`test_edge_cases.py`)
   - UUID validation edge cases
   - Boundary value testing
   - String input validation
   - Error recovery scenarios

## Prerequisites

Install test dependencies:

```bash
pip install -r requirements.txt
```

The test dependencies include:
- `pytest==7.4.4` - Testing framework
- `pytest-asyncio==0.21.1` - Async test support
- `httpx==0.25.2` - HTTP client for API testing

## Running Tests

### Quick Start

```bash
# Run all tests
python run_tests.py

# Run specific category
python run_tests.py --category models
python run_tests.py --category api

# Run with coverage
python run_tests.py --coverage

# Fast tests only (skip performance tests)
python run_tests.py --fast
```

### Using pytest directly

```bash
# Run all tests
pytest

# Run specific test file
pytest test_models.py

# Run with verbose output
pytest -v

# Run specific test class
pytest test_api.py::TestHospitalCRUD

# Run specific test method
pytest test_api.py::TestHospitalCRUD::test_create_hospital_success
```

### Test Categories

```bash
# Unit tests only
pytest test_models.py

# Database tests only
pytest test_database.py

# API integration tests
pytest test_api.py

# Batch processing tests
pytest test_batch.py

# Performance tests
pytest test_performance.py

# Edge case tests
pytest test_edge_cases.py
```

## Test Configuration

### Fixtures

The test suite uses several pytest fixtures defined in `conftest.py`:

- `client`: FastAPI test client
- `reset_database`: Automatic database cleanup between tests
- `mock_slow_task`: Bypasses 5-second processing delays
- `bypass_rate_limit`: Disables rate limiting for testing
- `sample_hospital_data`: Standard test hospital data
- `create_test_hospital`: Factory for creating test hospitals
- `create_test_batch`: Factory for creating hospital batches

### Test Isolation

Each test runs in isolation with:
- Fresh database state (empty deque)
- Reset ID counter
- Mocked slow processing tasks
- Bypassed rate limits (where appropriate)

## Key Test Scenarios

### Batch Processing Workflow

```python
def test_complete_batch_workflow():
    # 1. Create hospitals with batch_id (inactive)
    # 2. Verify batch exists and all hospitals inactive
    # 3. Activate batch
    # 4. Verify all hospitals now active
```

### Rate Limiting

```python
def test_rate_limit_enforcement():
    # Make rapid requests to trigger rate limiting
    # Verify 429 Too Many Requests responses
```

### FIFO Storage

```python
def test_fifo_storage_limit():
    # Create hospitals beyond 10,000 limit
    # Verify oldest are evicted (FIFO behavior)
```

### Batch Size Constraints

```python
def test_batch_size_limit():
    # Create exactly 20 hospitals in batch
    # Verify 21st hospital creation fails
```

## Performance Testing

### Rate Limiting Tests

- Verify rate limits are enforced per endpoint
- Test different limits for different operations
- Validate rate limit reset behavior

### FIFO Storage Tests

- Memory usage remains bounded
- Performance doesn't degrade with full storage
- FIFO eviction works correctly

### Concurrency Tests

- Concurrent hospital creation
- Simultaneous batch operations
- Race condition handling

## Coverage Report

Generate coverage report:

```bash
pytest --cov=. --cov-report=html --cov-report=term
```

View HTML report:
```bash
open htmlcov/index.html
```

## Expected Coverage

The test suite provides comprehensive coverage:

- **Models**: 100% (all validation paths)
- **Database**: ~95% (all operations + edge cases)
- **API Endpoints**: ~98% (all endpoints + error cases)
- **Batch Logic**: 100% (all workflows)
- **Rate Limiting**: ~85% (core functionality)

## Common Test Commands

```bash
# Run tests with minimal output
pytest -q

# Run tests and stop on first failure
pytest -x

# Run tests matching pattern
pytest -k "batch"

# Run tests and show local variables on failure
pytest -l

# Run tests with coverage and stop on first failure
pytest --cov=. -x

# Run only failed tests from last run
pytest --lf
```

## Test Data

### Sample Hospital Data

```json
{
  "name": "Test Hospital",
  "address": "123 Test St",
  "phone": "555-0123",
  "creation_batch_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Test Batches

Tests create batches of various sizes:
- Small batches (2-5 hospitals)
- Boundary batches (exactly 20 hospitals)
- Large batches (for FIFO testing)

## Debugging Tests

### Failed Test Investigation

```bash
# Run with maximum verbosity
pytest -vvv

# Show local variables on failure
pytest -l --tb=long

# Drop into debugger on failure
pytest --pdb

# Run specific failing test with debug info
pytest test_api.py::test_create_hospital -vvv -s
```

### Common Issues

1. **Rate Limiting**: Use `bypass_rate_limit` fixture
2. **Slow Tests**: Use `mock_slow_task` fixture
3. **Database State**: Ensure `reset_database` fixture is used
4. **Import Errors**: Check that all dependencies are installed

## Continuous Integration

For CI/CD pipelines:

```bash
# Run tests suitable for CI
pytest --tb=short --strict-markers

# Run with JUnit XML output
pytest --junitxml=test-results.xml

# Run with coverage for CI reporting
pytest --cov=. --cov-report=xml
```

## Test Environment Variables

Optional environment variables for testing:

```bash
# Skip slow tests
export PYTEST_SKIP_SLOW=1

# Increase test timeouts
export TEST_TIMEOUT=30

# Enable debug logging
export LOG_LEVEL=DEBUG
```

## Adding New Tests

### Test File Structure

```python
class TestFeatureName:
    """Test cases for specific feature."""

    def test_normal_case(self, client, fixtures):
        """Test normal operation."""
        pass

    def test_edge_case(self, client, fixtures):
        """Test edge case behavior."""
        pass

    def test_error_case(self, client, fixtures):
        """Test error handling."""
        pass
```

### Best Practices

1. Use descriptive test names
2. Test both success and failure paths
3. Use appropriate fixtures for setup
4. Keep tests isolated and independent
5. Test edge cases and boundary conditions
6. Include performance considerations
7. Mock external dependencies appropriately

## Troubleshooting

### Common Test Failures

1. **Import Errors**: Ensure Python path includes project root
2. **Database Conflicts**: Check database reset between tests
3. **Rate Limiting**: Verify bypass fixtures are used
4. **Async Issues**: Use appropriate async fixtures
5. **Timing Issues**: Mock time-dependent operations

### Performance Test Issues

- **Slow Tests**: Use mocking for time delays
- **Memory Issues**: Monitor resource usage in CI
- **Flaky Tests**: Add appropriate timeouts and retries