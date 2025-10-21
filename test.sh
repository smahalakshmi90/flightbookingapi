#!/bin/bash
# Flight Booking API Test Runner
# This script sets up the test database and runs all tests

echo "=========================================="
echo "🧪 Flight Booking API Test Suite"
echo "=========================================="
echo ""

# Activate virtual environment
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
else
    echo "⚠️  Virtual environment not found!"
    echo "💡 Run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Setup test database
echo "🔧 Setting up test database..."
python3 setup_test_db.py
if [ $? -ne 0 ]; then
    echo "❌ Failed to setup test database"
    exit 1
fi
echo ""

# Run tests
echo "=========================================="
echo "🚀 Running Tests"
echo "=========================================="
echo ""

# Run database tests
echo "📊 Database Tests:"
PYTHONPATH=. python3 test/database_api_tests_tables.py 2>&1 | grep -E "^Ran|^OK|^FAILED"
echo ""

# Run API tests  
echo "🌐 API Tests:"
PYTHONPATH=. python3 test/flight_booking_system_api_tests.py 2>&1 | grep -E "^Ran|^OK|^FAILED"
echo ""

echo "=========================================="
echo "✅ Tests completed!"
echo "=========================================="
echo ""
echo "💡 To run individual test files:"
echo "   PYTHONPATH=. python3 test/database_api_tests_user.py"
echo "   PYTHONPATH=. python3 test/flight_booking_system_api_tests.py"

