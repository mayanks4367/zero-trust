#!/bin/bash

# Black Box Vault - Mobile App Build Script
# This script helps build the Android app for deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Black Box Vault Mobile App${NC}"
echo -e "${BLUE}========================================${NC}"

# Function to print colored messages
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check dependencies
check_dependencies() {
    print_info "Checking dependencies..."
    
    # Check if we're in the right directory
    if [[ ! -f "main.py" ]]; then
        print_error "Please run this script from the vault_app directory"
        exit 1
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not found"
        exit 1
    fi
    
    print_success "Dependencies check passed"
}

# Setup virtual environment
setup_venv() {
    print_info "Setting up virtual environment..."
    
    if [[ ! -d "venv" ]]; then
        print_info "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate and install requirements
    print_info "Installing requirements..."
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    print_success "Virtual environment setup complete"
}

# Test the app locally
test_local() {
    print_info "Testing app locally..."
    
    source venv/bin/activate
    python3 main.py &
    local_pid=$!
    
    sleep 2
    if kill -0 $local_pid 2>/dev/null; then
        print_success "Local test passed"
        kill $local_pid 2>/dev/null
    else
        print_error "Local test failed"
        kill $local_pid 2>/dev/null
    fi
}

# Build for Android
build_android() {
    print_info "Building for Android..."
    
    source venv/bin/activate
    
    # Clean previous builds
    buildozer android clean
    
    # Build debug APK
    if buildozer android debug; then
        print_success "Android build completed"
        print_info "APK location: bin/"
        
        # Show APK info
        if [[ -f "bin/BlackBoxVault-1.0.0-debug.apk" ]]; then
            ls -lh "bin/BlackBoxVault-1.0.0-debug.apk"
            print_info "You can install this APK on your Android device"
        fi
    else
        print_error "Android build failed"
        return 1
    fi
}

# Deploy to device
deploy_android() {
    print_info "Deploying to Android device..."
    
    # Check if ADB is available
    if ! command -v adb &> /dev/null; then
        print_warning "ADB not found. Please install Android SDK platform tools"
        print_info "You can manually install the APK from bin/ directory"
        return 1
    fi
    
    # Check if device is connected
    if ! adb devices | grep -q "device$"; then
        print_warning "No Android device connected"
        print_info "Connect your device and enable USB debugging"
        return 1
    fi
    
    # Install the APK
    if adb install bin/BlackBoxVault-1.0.0-debug.apk; then
        print_success "App deployed successfully"
        print_info "You can now run the Black Box Vault app on your device"
    else
        print_error "Deployment failed"
        return 1
    fi
}

# Show usage information
show_usage() {
    echo ""
    echo -e "${GREEN}Black Box Vault Mobile App${NC}"
    echo "===================================="
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  test     - Test the app locally"
    echo "  build    - Build Android APK"
    echo "  deploy   - Build and deploy to connected device"
    echo "  clean    - Clean build artifacts"
    echo "  help     - Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 test      # Test the app in development mode"
    echo "  $0 build     # Build APK for Android"
    echo "  $0 deploy    # Build and install on connected device"
    echo ""
}

# Clean build artifacts
clean_build() {
    print_info "Cleaning build artifacts..."
    rm -rf bin/ .buildozer/ __pycache__/
    print_success "Clean completed"
}

# Main function
main() {
    case "${1:-help}" in
        "test")
            check_dependencies
            setup_venv
            test_local
            ;;
        "build")
            check_dependencies
            setup_venv
            build_android
            ;;
        "deploy")
            check_dependencies
            setup_venv
            build_android
            deploy_android
            ;;
        "clean")
            clean_build
            ;;
        "help"|"-h"|"--help")
            show_usage
            ;;
        *)
            print_error "Unknown command: $1"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"