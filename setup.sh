#!/bin/bash

# Black Box Vault - Installation Script
# This script sets up the complete Black Box Vault environment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEVICE_NAME="secret_vault"
PROJECT_NAME="Black Box Vault"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   $PROJECT_NAME Installation${NC}"
echo -e "${BLUE}========================================${NC}"

# Function to print colored messages
print_info() {
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

# Function to check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_warning "Running as root is not recommended for setup"
        print_info "Please run this script as a regular user with sudo access"
        exit 1
    fi
}

# Function to check system requirements
check_requirements() {
    print_info "Checking system requirements..."
    
    # Check if we're on Linux
    if [[ "$OSTYPE" != "linux-gnu"* ]]; then
        print_error "This system is not supported. Please use Linux."
        exit 1
    fi
    
    # Check for sudo access
    if ! sudo -n true 2>/dev/null; then
        print_info "This script requires sudo access for kernel module installation"
        print_info "Please enter your password when prompted"
    fi
    
    print_success "System requirements check passed"
}

# Function to install system dependencies
install_system_deps() {
    print_info "Installing system dependencies..."
    
    # Detect package manager
    if command -v apt-get &> /dev/null; then
        # Debian/Ubuntu
        print_info "Using apt package manager..."
        sudo apt-get update
        sudo apt-get install -y \
            python3 \
            python3-pip \
            python3-venv \
            build-essential \
            linux-headers-$(uname -r) \
            pkg-config
    elif command -v yum &> /dev/null; then
        # RHEL/CentOS/Fedora
        print_info "Using yum package manager..."
        sudo yum install -y \
            python3 \
            python3-pip \
            python3-venv \
            gcc \
            make \
            kernel-devel-$(uname -r) \
            pkgconfig
    elif command -v dnf &> /dev/null; then
        # Fedora
        print_info "Using dnf package manager..."
        sudo dnf install -y \
            python3 \
            python3-pip \
            python3-venv \
            gcc \
            make \
            kernel-devel-$(uname -r) \
            pkgconfig
    else
        print_error "Unsupported package manager. Please install dependencies manually."
        print_error "Required: python3, pip, build tools, kernel headers"
        exit 1
    fi
    
    print_success "System dependencies installed"
}

# Function to install Python dependencies
install_python_deps() {
    print_info "Installing Python dependencies..."
    
    # Install core requirements
    pip3 install --user opencv-python qrcode[pil]
    
    # Check installation
    if python3 -c "import cv2, qrcode" 2>/dev/null; then
        print_success "Core Python dependencies installed"
    else
        print_error "Failed to install Python dependencies"
        exit 1
    fi
    
    # Setup mobile app environment (optional)
    if [[ -d "vault_app" ]]; then
        print_info "Setting up mobile app environment..."
        cd vault_app
        
        if [[ ! -d "venv" ]]; then
            python3 -m venv venv
        fi
        
        source venv/bin/activate
        pip install -r ../requirements.txt 2>/dev/null || true
        cd ..
        print_success "Mobile app environment configured"
    fi
}

# Function to build kernel module
build_kernel_module() {
    print_info "Building kernel module..."
    
    # Clean previous builds
    make clean 2>/dev/null || true
    
    # Build the module
    if make; then
        print_success "Kernel module built successfully"
    else
        print_error "Failed to build kernel module"
        print_info "Please check that kernel headers are properly installed"
        exit 1
    fi
}

# Function to install kernel module
install_kernel_module() {
    print_info "Installing kernel module..."
    
    # Load the module
    if sudo insmod vault_driver.ko; then
        print_success "Kernel module loaded successfully"
    else
        print_error "Failed to load kernel module"
        print_info "Check kernel logs with: dmesg | tail -20"
        exit 1
    fi
    
    # Get major device number
    MAJOR=$(grep vault_driver /proc/devices | awk '{print $1}')
    
    if [[ -z "$MAJOR" ]]; then
        print_error "Could not find device major number"
        exit 1
    fi
    
    # Create device node
    print_info "Creating device node..."
    sudo mknod /dev/$DEVICE_NAME c $MAJOR 0
    sudo chmod 666 /dev/$DEVICE_NAME
    
    print_success "Device node created: /dev/$DEVICE_NAME"
}

# Function to verify installation
verify_installation() {
    print_info "Verifying installation..."
    
    # Check if module is loaded
    if lsmod | grep -q vault_driver; then
        print_success "✓ Kernel module is loaded"
    else
        print_error "✗ Kernel module not found"
        return 1
    fi
    
    # Check device node
    if [[ -e "/dev/$DEVICE_NAME" ]]; then
        print_success "✓ Device node exists"
    else
        print_error "✗ Device node not found"
        return 1
    fi
    
    # Test Python dependencies
    if python3 -c "import cv2, qrcode" 2>/dev/null; then
        print_success "✓ Python dependencies working"
    else
        print_error "✗ Python dependencies not working"
        return 1
    fi
    
    print_success "Installation verification completed"
}

# Function to show usage instructions
show_usage() {
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}   Installation Complete!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "${BLUE}Quick Start:${NC}"
    echo "1. Run the guard script:"
    echo "   ${YELLOW}python3 guard.py${NC}"
    echo ""
    echo "2. Generate QR code:"
    echo "   ${YELLOW}python3 -m http.server 8000${NC}"
    echo "   Then open: http://localhost:8000/index.html"
    echo ""
    echo "3. Test vault access:"
    echo "   ${YELLOW}echo 'test_secret' > /dev/$DEVICE_NAME${NC}"
    echo "   ${YELLOW}cat /dev/$DEVICE_NAME${NC}"
    echo ""
    echo -e "${BLUE}Uninstallation:${NC}"
    echo "   ${YELLOW}sudo rmmod vault_driver${NC}"
    echo "   ${YELLOW}sudo rm /dev/$DEVICE_NAME${NC}"
    echo ""
    echo -e "${BLUE}For more information, see README.md${NC}"
}

# Main installation flow
main() {
    echo "Starting $PROJECT_NAME installation..."
    echo ""
    
    check_root
    check_requirements
    install_system_deps
    install_python_deps
    build_kernel_module
    install_kernel_module
    verify_installation
    show_usage
    
    echo ""
    print_success "$PROJECT_NAME has been successfully installed!"
}

# Handle script interruption
trap 'print_error "Installation interrupted"; exit 1' INT TERM

# Run main function
main "$@"