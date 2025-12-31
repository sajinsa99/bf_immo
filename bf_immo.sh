#!/bin/bash

# bf_immo.sh - Control script for DVF data analysis and web server
# Usage: ./bf_immo.sh {start|stop|status}

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DVF_DIR="$SCRIPT_DIR/dvf_files"
PORT=8888
PID_FILE="$SCRIPT_DIR/.http_server.pid"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status messages
log_info() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✘${NC} $1"
}

# Function to download DVF files if not already present
download_dvf_files() {
    local year_range="${1:-2020-2025}"
    
    if [ -f "$SCRIPT_DIR/data.json" ] && [ -z "$1" ]; then
        log_info "Data file already exists (use year range to re-fetch)"
        return 0
    fi
    
    log_info "Fetching real estate data from LePrixImmo (years: $year_range)..."
    cd "$SCRIPT_DIR"
    
    # Check if virtual environment exists, create if not
    if [ ! -d "venv" ]; then
        log_info "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate venv and install dependencies
    # shellcheck disable=SC1091
    source venv/bin/activate
    log_info "Installing dependencies..."
    pip install -q -r requirements.txt 2>/dev/null || true
    
    # Run the scraper script with year range
    log_info "Scraping and analyzing real estate data..."
    python3 fetch_lepriximmo.py "$year_range"
    
    deactivate
    log_info "Data fetch completed"
}

# Function to start the HTTP server
start_server() {
    if [ -f "$PID_FILE" ]; then
        local old_pid
        old_pid=$(cat "$PID_FILE")
        if kill -0 "$old_pid" 2>/dev/null; then
            log_warn "Server is already running (PID: $old_pid)"
            return 0
        fi
    fi
    
    log_info "Starting HTTP server on port $PORT..."
    cd "$SCRIPT_DIR"
    
    # Create a temporary Python server script with no-cache headers for data.json
    cat > /tmp/bf_immo_server.py << 'EOF'
#!/usr/bin/env python3
import http.server
import socketserver
import sys
from pathlib import Path

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8888

class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add no-cache headers for dynamic files
        if self.path.endswith('.json') or self.path == '/':
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
        super().end_headers()

handler = NoCacheHandler
with socketserver.TCPServer(("", PORT), handler) as httpd:
    print(f"Server running on port {PORT}", flush=True)
    httpd.serve_forever()
EOF
    
    # Start server in background and save PID
    python3 /tmp/bf_immo_server.py $PORT > /tmp/bf_immo_server.log 2>&1 &
    echo $! > "$PID_FILE"
    
    sleep 1
    
    if kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        log_info "HTTP server started successfully (PID: $(cat "$PID_FILE"))"
        log_info "Access at: http://localhost:$PORT"
    else
        log_error "Failed to start HTTP server"
        return 1
    fi
}

# Function to stop the HTTP server
stop_server() {
    if [ ! -f "$PID_FILE" ]; then
        log_warn "No server PID file found"
        return 0
    fi
    
    local pid
    pid=$(cat "$PID_FILE")
    
    if kill -0 "$pid" 2>/dev/null; then
        log_info "Stopping HTTP server (PID: $pid)..."
        kill "$pid"
        sleep 1
        rm -f "$PID_FILE"
        log_info "HTTP server stopped"
    else
        log_warn "Server process not found (PID: $pid)"
        rm -f "$PID_FILE"
    fi
}

# Function to check server status
check_status() {
    if [ ! -f "$PID_FILE" ]; then
        log_warn "Server is not running"
        return 1
    fi
    
    local pid
    pid=$(cat "$PID_FILE")
    
    if kill -0 "$pid" 2>/dev/null; then
        log_info "Server is running (PID: $pid) on port $PORT"
        log_info "Access at: http://localhost:$PORT"
    else
        log_warn "Server PID file exists but process not running"
        rm -f "$PID_FILE"
        return 1
    fi
}

# Function to restart the server
restart_server() {
    log_info "Restarting server..."
    stop_server
    sleep 1
    start_server
}

# Main command handler
main() {
    case "${1:-}" in
        start)
            download_dvf_files "${2:-}"
            start_server
            ;;
        stop)
            stop_server
            ;;
        restart|reload)
            restart_server
            ;;
        status)
            check_status
            ;;
        *)
            echo "Usage: $0 {start|stop|restart|status} [year_range]"
            echo ""
            echo "Commands:"
            echo "  start [RANGE]   - Download data and start HTTP server on port 8888"
            echo "                    RANGE format: YYYY-YYYY (e.g., 2020-2025)"
            echo "  stop            - Stop the HTTP server"
            echo "  restart|reload  - Restart the HTTP server"
            echo "  status          - Show server status"
            echo ""
            echo "Examples:"
            echo "  $0 start              # Fetch default years (2020-2025)"
            echo "  $0 start 2020-2025    # Fetch years 2020 to 2025"
            echo "  $0 restart            # Restart the server"
            exit 1
            ;;
    esac
}

main "$@"
