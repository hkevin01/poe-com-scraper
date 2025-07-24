#!/bin/bash

# Poe.com Scraper - GUI Launcher Script
# This script runs the Poe.com Scraper GUI by default

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Activate Python virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    PYTHON_BIN="$(pwd)/venv/bin/python"
    echo "[INFO] Activated Python virtual environment. Using: $PYTHON_BIN"
else
    PYTHON_BIN="python3"
    echo "[WARNING] venv not found. Using system Python: $PYTHON_BIN"
fi

# Function to check if Python is installed
check_python() {
    if command -v "$PYTHON_BIN" &> /dev/null; then
        print_status "Using Python: $($PYTHON_BIN --version)"
    else
        print_error "Python is not installed or not in PATH"
        exit 1
    fi
}

# Function to check if required packages are installed
check_requirements() {
    print_status "Checking requirements..."
    
    if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
        if ! $PYTHON_BIN -c "
import pkg_resources
import sys

try:
    with open('$PROJECT_ROOT/requirements.txt', 'r') as f:
        requirements = f.read().splitlines()
    
    # Filter out comments and empty lines
    requirements = [req.strip() for req in requirements if req.strip() and not req.strip().startswith('#')]
    
    for requirement in requirements:
        try:
            pkg_resources.require(requirement)
        except pkg_resources.DistributionNotFound:
            print(f'Missing: {requirement}')
            sys.exit(1)
        except pkg_resources.VersionConflict as e:
            print(f'Version conflict: {e}')
            sys.exit(1)
    
    print('All requirements satisfied')
except Exception as e:
    print(f'Error checking requirements: {e}')
    sys.exit(1)
" 2>/dev/null; then
            print_warning "Some requirements are missing. Installing..."
            install_requirements
        else
            print_success "All requirements satisfied"
        fi
    else
        print_warning "requirements.txt not found. Attempting to run anyway..."
    fi
}

# Function to install requirements
install_requirements() {
    print_status "Installing requirements..."
    
    if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
        $PYTHON_BIN -m pip install -r "$PROJECT_ROOT/requirements.txt"
        if [ $? -eq 0 ]; then
            print_success "Requirements installed successfully"
        else
            print_error "Failed to install requirements"
            exit 1
        fi
    else
        print_error "requirements.txt not found"
        exit 1
    fi
}

# Function to check if GUI dependencies are available
check_gui_dependencies() {
    print_status "Checking GUI dependencies..."
    
    $PYTHON_BIN -c "
import sys
try:
    import tkinter
    print('tkinter: OK')
except ImportError:
    print('tkinter: MISSING - GUI cannot run without tkinter')
    sys.exit(1)

try:
    import tkinter.ttk
    print('tkinter.ttk: OK')
except ImportError:
    print('tkinter.ttk: MISSING - Enhanced GUI features may not work')

# Check other GUI-related dependencies
optional_deps = ['asyncio', 'threading', 'json', 'os', 'logging']
for dep in optional_deps:
    try:
        __import__(dep)
        print(f'{dep}: OK')
    except ImportError:
        print(f'{dep}: MISSING')
        sys.exit(1)
"
    
    if [ $? -eq 0 ]; then
        print_success "GUI dependencies check passed"
    else
        print_error "GUI dependencies check failed"
        exit 1
    fi
}

# Function to run the GUI
run_gui() {
    print_status "Starting Poe.com Scraper GUI..."
    
    # Change to project root directory
    cd "$PROJECT_ROOT"
    
    # Add src directory to Python path and run the GUI
    export PYTHONPATH="$PROJECT_ROOT/src:$PYTHONPATH"
    
    # Try different ways to run the GUI
    if [ -f "$PROJECT_ROOT/src/gui.py" ]; then
        print_status "Running GUI from src/gui.py..."
        $PYTHON_BIN -c "
import sys
sys.path.insert(0, '$PROJECT_ROOT/src')
from gui import main
main()
"
    elif [ -f "$PROJECT_ROOT/src/__init__.py" ]; then
        print_status "Running GUI from package..."
        $PYTHON_BIN -c "
import sys
sys.path.insert(0, '$PROJECT_ROOT')
from src.gui import main
main()
"
    else
        print_error "GUI module not found. Please ensure src/gui.py exists."
        exit 1
    fi
}

# Function to show usage
show_usage() {
    echo "Poe.com Scraper - Run Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "OPTIONS:"
    echo "  --help, -h          Show this help message"
    echo "  --install, -i       Install/update requirements only"
    echo "  --check, -c         Check dependencies only"
    echo "  --cli               Run in CLI mode (not implemented yet)"
    echo "  --version, -v       Show version information"
    echo ""
    echo "By default, this script runs the GUI version of the scraper."
    echo ""
    echo "Examples:"
    echo "  $0                  # Run GUI (default)"
    echo "  $0 --install        # Install requirements"
    echo "  $0 --check          # Check dependencies"
}

# Function to show version
show_version() {
    print_status "Poe.com Scraper"
    if [ -f "$PROJECT_ROOT/src/__init__.py" ]; then
        VERSION=$($PYTHON_BIN -c "
import sys
sys.path.insert(0, '$PROJECT_ROOT/src')
try:
    from __init__ import __version__
    print(__version__)
except:
    print('Unknown')
" 2>/dev/null)
        echo "Version: $VERSION"
    else
        echo "Version: Unknown"
    fi
    echo "Project: https://github.com/hkevin01/poe-com-scraper"
}

# Main execution logic
main() {
    # Print banner
    echo ""
    echo "=============================================="
    echo "    Poe.com Scraper - GUI Launcher"
    echo "=============================================="
    echo ""
    
    # Parse command line arguments
    case "${1:-}" in
        --help|-h)
            show_usage
            exit 0
            ;;
        --version|-v)
            show_version
            exit 0
            ;;
        --install|-i)
            check_python
            install_requirements
            exit 0
            ;;
        --check|-c)
            check_python
            check_requirements
            check_gui_dependencies
            print_success "All checks passed"
            exit 0
            ;;
        --cli)
            print_error "CLI mode not implemented yet. Use GUI mode."
            exit 1
            ;;
        "")
            # Default behavior - run GUI
            print_status "Running in GUI mode (default)"
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
    
    # Pre-flight checks
    check_python
    check_requirements
    check_gui_dependencies
    
    # Run the GUI
    run_gui
    
    if [ $? -eq 0 ]; then
        print_success "GUI session completed"
    else
        print_error "GUI session ended with errors"
        exit 1
    fi
}

# Trap to handle script interruption
trap 'print_warning "Script interrupted by user"; exit 130' INT

# Run main function with all arguments
main "$@"