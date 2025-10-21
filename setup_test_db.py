#!/usr/bin/env python3
"""
Setup test database for Flight Booking API tests
Creates a fresh test database with schema and sample data
"""
import os
import sqlite3
import sys

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flight_reservation import flight_database as database

TEST_DB_PATH = 'db/flight_test.db'

print("🔧 Setting up test database...")
print(f"📁 Database path: {TEST_DB_PATH}")

# Remove existing test database
if os.path.exists(TEST_DB_PATH):
    print(f"🗑️  Removing existing test database...")
    os.remove(TEST_DB_PATH)

# Create fresh test database
print("✨ Creating new test database with schema and data...")
try:
    engine = database.Engine(TEST_DB_PATH)
    engine.create_tables()
    engine.populate_tables()
    print("✅ Test database created successfully!")
    print(f"📊 Location: {os.path.abspath(TEST_DB_PATH)}")
except Exception as e:
    print(f"❌ Error creating test database: {e}")
    sys.exit(1)

