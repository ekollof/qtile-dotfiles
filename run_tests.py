#!/usr/bin/env python3
"""
Test runner script for Qtile configuration tests

@brief Convenient script to run pytest with proper configuration
"""

import subprocess
import sys
from pathlib import Path


def run_tests(args: list[str] | None = None) -> int:
    """Run pytest with the given arguments"""
    if args is None:
        args = []

    # Ensure we're in the correct directory
    qtile_config_dir = Path(__file__).parent
    if not qtile_config_dir.exists():
        print(f"Error: Qtile config directory not found: {qtile_config_dir}")
        return 1

    # Change to the qtile config directory
    import os

    os.chdir(qtile_config_dir)

    # Build pytest command
    cmd = [sys.executable, "-m", "pytest", *args]

    print(f"Running: {' '.join(cmd)}")
    print(f"Working directory: {qtile_config_dir}")

    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except KeyboardInterrupt:
        print("\nTest run interrupted by user")
        return 130
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Run Qtile configuration tests")
    parser.add_argument(
        "--coverage", action="store_true", help="Run tests with coverage reporting"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "--unit-only",
        action="store_true",
        help="Run only unit tests (exclude integration tests)",
    )
    parser.add_argument(
        "--integration-only", action="store_true", help="Run only integration tests"
    )
    parser.add_argument(
        "--no-cov", action="store_true", help="Disable coverage reporting"
    )
    parser.add_argument(
        "pytest_args", nargs="*", help="Additional arguments to pass to pytest"
    )

    args = parser.parse_args()

    # Build pytest arguments
    pytest_args = []

    if args.verbose:
        pytest_args.append("-v")

    if args.unit_only:
        pytest_args.extend(["-m", "unit"])
    elif args.integration_only:
        pytest_args.extend(["-m", "integration"])

    if args.no_cov:
        # Remove coverage from pytest.ini defaults
        pytest_args.extend(["--no-cov"])
    elif args.coverage:
        pytest_args.extend(
            ["--cov=modules", "--cov-report=term-missing", "--cov-report=html:htmlcov"]
        )

    # Add any additional pytest arguments
    pytest_args.extend(args.pytest_args)

    # Run the tests
    exit_code = run_tests(pytest_args)

    if exit_code == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ Tests failed with exit code: {exit_code}")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
