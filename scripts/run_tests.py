#!/usr/bin/env python3
"""
Test runner script for the Hospital Directory API.

This script provides different test execution options:
- Run all tests
- Run specific test categories
- Run with different verbosity levels
- Generate coverage reports
"""

import subprocess
import sys
import argparse
from pathlib import Path


def run_command(cmd, description=""):
    """Run a command and handle errors."""
    if description:
        print(f"\n{description}")
        print("-" * len(description))

    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(description="Run Hospital Directory API tests")
    parser.add_argument(
        "--category",
        choices=["models", "database", "api", "batch", "performance", "edge", "all"],
        default="all",
        help="Test category to run"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run with coverage report"
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Skip slow tests (performance tests)"
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Run tests in parallel (requires pytest-xdist)"
    )

    args = parser.parse_args()

    # Build pytest command
    cmd = ["python", "-m", "pytest"]

    # Add verbosity
    if args.verbose:
        cmd.extend(["-v", "-s"])

    # Add coverage
    if args.coverage:
        cmd.extend(["--cov=.", "--cov-report=html", "--cov-report=term"])

    # Add parallel execution
    if args.parallel:
        cmd.extend(["-n", "auto"])

    # Skip slow tests if requested
    if args.fast:
        cmd.extend(["-m", "not slow"])

    # Add specific test files based on category
    if args.category != "all":
        test_files = {
            "models": "test_models.py",
            "database": "test_database.py",
            "api": "test_api.py",
            "batch": "test_batch.py",
            "performance": "test_performance.py",
            "edge": "test_edge_cases.py"
        }
        cmd.append(test_files[args.category])

    # Check if pytest is available
    try:
        subprocess.run(["python", "-m", "pytest", "--version"],
                      check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("Error: pytest not found. Please install test dependencies:")
        print("pip install -r requirements.txt")
        sys.exit(1)

    # Run tests
    print("Hospital Directory API Test Suite")
    print("=" * 50)

    success = run_command(cmd, f"Running {args.category} tests")

    if success:
        print("\n✅ All tests passed!")
        if args.coverage:
            print("📊 Coverage report generated in htmlcov/index.html")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()