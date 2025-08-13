#!/bin/bash

# CashFlow 2.0 Integration Test Runner
# This script runs comprehensive integration tests for the frontend-backend integration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
BACKEND_DIR="$PROJECT_ROOT/backend"
TEST_RESULTS_DIR="$PROJECT_ROOT/test-results"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Create test results directory
mkdir -p "$TEST_RESULTS_DIR"

echo -e "${BLUE}🚀 CashFlow 2.0 Integration Test Runner${NC}"
echo -e "${BLUE}========================================${NC}"
echo "Project Root: $PROJECT_ROOT"
echo "Frontend Dir: $FRONTEND_DIR"
echo "Backend Dir: $BACKEND_DIR"
echo "Test Results: $TEST_RESULTS_DIR"
echo "Timestamp: $TIMESTAMP"
echo ""

# Function to print status
print_status() {
    local status=$1
    local message=$2
    case $status in
        "info")
            echo -e "${BLUE}ℹ️  $message${NC}"
            ;;
        "success")
            echo -e "${GREEN}✅ $message${NC}"
            ;;
        "warning")
            echo -e "${YELLOW}⚠️  $message${NC}"
            ;;
        "error")
            echo -e "${RED}❌ $message${NC}"
            ;;
    esac
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
print_status "info" "Checking prerequisites..."

if ! command_exists node; then
    print_status "error" "Node.js is not installed. Please install Node.js 18+ and try again."
    exit 1
fi

if ! command_exists npm; then
    print_status "error" "npm is not installed. Please install npm and try again."
    exit 1
fi

if ! command_exists python3; then
    print_status "error" "Python 3 is not installed. Please install Python 3.8+ and try again."
    exit 1
fi

print_status "success" "Prerequisites check passed"

# Check if we're in the right directory
if [[ ! -f "$FRONTEND_DIR/package.json" ]]; then
    print_status "error" "Frontend package.json not found. Please run this script from the project root."
    exit 1
fi

if [[ ! -f "$BACKEND_DIR/requirements.txt" ]]; then
    print_status "error" "Backend requirements.txt not found. Please run this script from the project root."
    exit 1
fi

print_status "success" "Project structure verified"

# Install frontend dependencies
print_status "info" "Installing frontend dependencies..."
cd "$FRONTEND_DIR"
if [[ ! -d "node_modules" ]]; then
    npm install
    print_status "success" "Frontend dependencies installed"
else
    print_status "info" "Frontend dependencies already installed"
fi

# Install backend dependencies
print_status "info" "Installing backend dependencies..."
cd "$BACKEND_DIR"
if [[ ! -d "venv" ]]; then
    print_status "info" "Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt
print_status "success" "Backend dependencies installed"

# Return to project root
cd "$PROJECT_ROOT"

# Run backend health check
print_status "info" "Checking backend health..."
cd "$BACKEND_DIR"
source venv/bin/activate

# Start backend server in background
print_status "info" "Starting backend server..."
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > "$TEST_RESULTS_DIR/backend.log" 2>&1 &
BACKEND_PID=$!

# Wait for backend to start
print_status "info" "Waiting for backend to start..."
sleep 10

# Check if backend is responding
if curl -s http://localhost:8000/health > /dev/null; then
    print_status "success" "Backend server is running and healthy"
else
    print_status "error" "Backend server is not responding"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

# Return to project root
cd "$PROJECT_ROOT"

# Run frontend tests
print_status "info" "Running frontend unit tests..."
cd "$FRONTEND_DIR"
npm test -- --passWithNoTests --watchAll=false > "$TEST_RESULTS_DIR/frontend-unit-tests.log" 2>&1
FRONTEND_TEST_EXIT_CODE=$?

if [[ $FRONTEND_TEST_EXIT_CODE -eq 0 ]]; then
    print_status "success" "Frontend unit tests passed"
else
    print_status "warning" "Frontend unit tests had issues (check logs)"
fi

# Run integration tests
print_status "info" "Running integration tests..."
cd "$FRONTEND_DIR"

# Run Jest integration tests
npm test -- --testPathPattern="integration" --passWithNoTests --watchAll=false > "$TEST_RESULTS_DIR/integration-tests.log" 2>&1
INTEGRATION_TEST_EXIT_CODE=$?

if [[ $INTEGRATION_TEST_EXIT_CODE -eq 0 ]]; then
    print_status "success" "Integration tests passed"
else
    print_status "warning" "Integration tests had issues (check logs)"
fi

# Run E2E tests
print_status "info" "Running end-to-end tests..."
npm test -- --testPathPattern="e2e" --passWithNoTests --watchAll=false > "$TEST_RESULTS_DIR/e2e-tests.log" 2>&1
E2E_TEST_EXIT_CODE=$?

if [[ $E2E_TEST_EXIT_CODE -eq 0 ]]; then
    print_status "success" "E2E tests passed"
else
    print_status "warning" "E2E tests had issues (check logs)"
fi

# Stop backend server
print_status "info" "Stopping backend server..."
kill $BACKEND_PID 2>/dev/null || true
sleep 2

# Generate test summary
print_status "info" "Generating test summary..."

cd "$PROJECT_ROOT"

# Create test summary
cat > "$TEST_RESULTS_DIR/test-summary.md" << EOF
# CashFlow 2.0 Integration Test Summary

**Timestamp:** $TIMESTAMP  
**Project Root:** $PROJECT_ROOT

## Test Results

### Frontend Unit Tests
- **Status:** $([ $FRONTEND_TEST_EXIT_CODE -eq 0 ] && echo "✅ PASSED" || echo "❌ FAILED")
- **Log File:** frontend-unit-tests.log

### Integration Tests
- **Status:** $([ $INTEGRATION_TEST_EXIT_CODE -eq 0 ] && echo "✅ PASSED" || echo "❌ FAILED")
- **Log File:** integration-tests.log

### End-to-End Tests
- **Status:** $([ $E2E_TEST_EXIT_CODE -eq 0 ] && echo "✅ PASSED" || echo "❌ FAILED")
- **Log File:** e2e-tests.log

## Backend Status
- **Server:** Started successfully
- **Health Check:** ✅ PASSED
- **Log File:** backend.log

## Next Steps

1. Review test logs in the \`test-results\` directory
2. Fix any failing tests
3. Run tests again to verify fixes
4. Proceed with deployment when all tests pass

## Files Generated

- \`frontend-unit-tests.log\` - Frontend unit test results
- \`integration-tests.log\` - Integration test results  
- \`e2e-tests.log\` - End-to-end test results
- \`backend.log\` - Backend server logs
- \`test-summary.md\` - This summary file

EOF

# Print final summary
echo ""
echo -e "${BLUE}📊 INTEGRATION TEST SUMMARY${NC}"
echo -e "${BLUE}==========================${NC}"
echo "Frontend Unit Tests: $([ $FRONTEND_TEST_EXIT_CODE -eq 0 ] && echo "✅ PASSED" || echo "❌ FAILED")"
echo "Integration Tests: $([ $INTEGRATION_TEST_EXIT_CODE -eq 0 ] && echo "✅ PASSED" || echo "❌ FAILED")"
echo "E2E Tests: $([ $E2E_TEST_EXIT_CODE -eq 0 ] && echo "✅ PASSED" || echo "❌ FAILED")"
echo "Backend Health: ✅ PASSED"
echo ""
echo "Test results saved to: $TEST_RESULTS_DIR"
echo "Summary file: $TEST_RESULTS_DIR/test-summary.md"
echo ""

# Determine overall success
if [[ $FRONTEND_TEST_EXIT_CODE -eq 0 && $INTEGRATION_TEST_EXIT_CODE -eq 0 && $E2E_TEST_EXIT_CODE -eq 0 ]]; then
    print_status "success" "🎉 All integration tests completed successfully!"
    print_status "success" "The CashFlow 2.0 application is ready for production deployment."
    exit 0
else
    print_status "warning" "⚠️  Some tests failed. Please review the logs and fix the issues."
    print_status "info" "Check the test results in: $TEST_RESULTS_DIR"
    exit 1
fi
