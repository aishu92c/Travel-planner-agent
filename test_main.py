#!/usr/bin/env python3
"""Test script for src/main.py module.

This script tests:
1. Import of the module
2. CLI argument parsing
3. Function signatures
4. Help output
"""

import sys
import subprocess

def test_imports():
    """Test that the module can be imported."""
    print("Testing imports...")
    try:
        from src.main import (
            run_travel_planner,
            create_cli_parser,
            main,
            format_budget_breakdown,
            format_selected_option,
            format_itinerary,
            format_state_summary,
        )
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_cli_parser():
    """Test the CLI parser creation."""
    print("\nTesting CLI parser creation...")
    try:
        from src.main import create_cli_parser
        parser = create_cli_parser()
        print("✓ CLI parser created successfully")
        return True
    except Exception as e:
        print(f"✗ Parser creation failed: {e}")
        return False


def test_cli_help():
    """Test the CLI help output."""
    print("\nTesting CLI help output...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "src.main", "--help"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and ("Travel Planner" in result.stdout or "usage" in result.stdout):
            print("✓ CLI help output works")
            return True
        else:
            print(f"✗ CLI help output failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("✗ CLI help timed out")
        return False
    except Exception as e:
        print(f"✗ CLI help test failed: {e}")
        return False


def test_cli_plan_help():
    """Test the plan subcommand help."""
    print("\nTesting 'plan' subcommand help...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "src.main", "plan", "--help"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and "destination" in result.stdout:
            print("✓ Plan subcommand help works")
            return True
        else:
            print(f"✗ Plan subcommand help failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("✗ Plan subcommand help timed out")
        return False
    except Exception as e:
        print(f"✗ Plan subcommand help test failed: {e}")
        return False


def main_test():
    """Run all tests."""
    print("=" * 70)
    print("Testing src/main.py Module")
    print("=" * 70)

    results = [
        ("Module Imports", test_imports()),
        ("CLI Parser", test_cli_parser()),
        ("CLI Help", test_cli_help()),
        ("Plan Subcommand Help", test_cli_plan_help()),
    ]

    print("\n" + "=" * 70)
    print("Test Results Summary")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name:<30} {status}")

    print("=" * 70)
    print(f"Total: {passed}/{total} tests passed")
    print("=" * 70)

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main_test())

