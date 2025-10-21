#!/usr/bin/env python3
"""
Test runner for Flight Booking API
Runs all unit tests and displays a summary
"""
import os
import sys
import unittest
import sqlite3

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Note: Test database should be set up first using setup_test_db.py
TEST_DB_PATH = 'db/flight_test.db'
if not os.path.exists(TEST_DB_PATH):
    print(f"⚠️  Test database not found: {TEST_DB_PATH}")
    print(f"💡 Run: python3 setup_test_db.py\n")

print("=" * 60)
print("🧪 Flight Booking API - Test Suite")
print("=" * 60)
print()

# Discover and run all tests
loader = unittest.TestLoader()
start_dir = 'test'
suite = loader.discover(start_dir, pattern='database_api_tests_*.py')

# Run tests with verbosity
runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)

print()
print("=" * 60)
print("📊 Test Summary")
print("=" * 60)
print(f"Tests run: {result.testsRun}")
print(f"✅ Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
print(f"❌ Failed: {len(result.failures)}")
print(f"⚠️  Errors: {len(result.errors)}")
print()

# Exit with appropriate code
sys.exit(0 if result.wasSuccessful() else 1)

