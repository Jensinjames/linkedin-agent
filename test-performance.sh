#!/bin/bash
# Build Performance Testing Script
# Tests and benchmarks different build strategies

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Function to time a command
time_command() {
    local description="$1"
    shift
    log_step "Starting: $description"
    
    start_time=$(date +%s)
    if "$@"; then
        end_time=$(date +%s)
        duration=$((end_time - start_time))
        log_info "✅ $description completed in ${duration}s"
        return 0
    else
        end_time=$(date +%s)
        duration=$((end_time - start_time))
        log_error "❌ $description failed after ${duration}s"
        return 1
    fi
}

# Test local development setup
test_local_setup() {
    log_step "Testing local development setup..."
    
    cd "$(dirname "$0")"
    
    # Test backend local installation
    if time_command "Backend dependency installation" pip install -r backend/requirements-dev.txt --user --quiet; then
        log_info "Backend dependencies installed successfully"
    else
        log_warn "Backend dependency installation had issues (may be due to missing system packages)"
    fi
    
    # Test frontend installation
    if command -v npm >/dev/null 2>&1; then
        cd frontend
        if time_command "Frontend dependency installation" npm install --silent; then
            log_info "Frontend dependencies installed successfully"
        fi
        
        if time_command "Frontend build test" npm run build; then
            log_info "Frontend builds successfully"
        fi
        cd ..
    else
        log_warn "npm not found, skipping frontend tests"
    fi
    
    # Test backend import
    cd backend
    if time_command "Backend import test" python -c "import src.server; print('Backend imports successfully')"; then
        log_info "Backend imports working"
    fi
    cd ..
}

# Test Docker builds
test_docker_builds() {
    log_step "Testing Docker builds..."
    
    cd "$(dirname "$0")/backend"
    
    # Test development build
    if command -v docker >/dev/null 2>&1; then
        if time_command "Docker development build" docker build -f Dockerfile.dev -t linkedin-agent:dev-test . --quiet; then
            log_info "Development Docker build successful"
            docker rmi linkedin-agent:dev-test >/dev/null 2>&1 || true
        else
            log_warn "Development Docker build failed (may be due to network/SSL issues)"
        fi
        
        if time_command "Docker production build" docker build -f Dockerfile.prod -t linkedin-agent:prod-test . --quiet; then
            log_info "Production Docker build successful"
            docker rmi linkedin-agent:prod-test >/dev/null 2>&1 || true
        else
            log_warn "Production Docker build failed (may be due to network/SSL issues)"
        fi
    else
        log_warn "Docker not found, skipping Docker build tests"
    fi
}

# Run performance benchmarks
run_benchmarks() {
    log_step "Running performance benchmarks..."
    
    # Frontend build benchmark
    if command -v npm >/dev/null 2>&1; then
        cd "$(dirname "$0")/frontend"
        if [[ -f package.json ]]; then
            log_step "Frontend build benchmark (3 runs):"
            
            for i in {1..3}; do
                rm -rf dist/ 2>/dev/null || true
                time_command "Frontend build #$i" npm run build --silent
            done
        else
            log_warn "Frontend package.json not found"
        fi
        cd ..
    fi
    
    # Backend startup benchmark
    cd "$(dirname "$0")/backend"
    log_step "Backend startup benchmark:"
    time_command "Backend startup test" timeout 10s python -c "
import src.server
import time
start = time.time()
app = src.server.app
print(f'Backend app initialized in {time.time() - start:.2f}s')
" 2>/dev/null || log_warn "Backend startup test timed out (may need Redis)"
}

# Main execution
main() {
    echo "🚀 LinkedIn Agent - Performance Testing Suite"
    echo "============================================="
    
    log_info "Starting comprehensive performance tests..."
    
    test_local_setup
    echo ""
    
    test_docker_builds  
    echo ""
    
    run_benchmarks
    echo ""
    
    log_info "🎉 Performance testing complete!"
    log_info "💡 For best development performance, use: make dev-local"
    log_info "🐳 For production builds, use: make deploy"
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi