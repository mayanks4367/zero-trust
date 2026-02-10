# 🔐 Black Box Vault - Zero-Trust Secret Vault System

A multi-component zero-trust secret vault system that combines Linux kernel security with QR code authentication for secure secret storage and access.

## 🎯 Overview

The Black Box Vault implements a secure, hardware-isolated secret storage system with automatic locking, requiring both kernel-level permissions and QR code-based authentication. This multi-layered approach ensures that secrets remain protected even if one component is compromised.

### 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web/Mobile   │    │   Guard Script  │    │  Kernel Module  │
│   QR Display   │───▶│   (Eyes/Brain)  │───▶│  (Vault Core)   │
│                │    │                 │    │                 │
│ - index.html   │    │ - QR Detection  │    │ - /dev/secret   │
│ - Android App  │    │ - Validation    │    │ - PIN Auth      │
│ - QR Code      │    │ - IOCTL Calls   │    │ - Auto-Lock     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Features

- **🔒 Kernel-Level Security**: Secrets stored in kernel space, isolated from user-space attacks
- **📱 Multi-Platform Access**: Web interface and Android app for QR code display
- **👁️ Visual Authentication**: QR code scanning with real-time feedback
- **⏰ Auto-Lock**: Automatic 30-second timeout to prevent unauthorized access
- **🛡️ Zero-Trust**: Requires both PIN and QR code authentication
- **📊 Rate Limiting**: Protection against brute-force attacks
- **🔄 Cross-Platform**: Works on Linux with webcam support

## 📁 Project Structure

```
black_box_vault/
├── vault_driver.c          # Linux kernel module (core vault)
├── guard.py                # QR code detection & authentication
├── index.html              # Web-based QR code interface
├── Makefile               # Kernel build system
├── requirements.txt       # Python dependencies
├── vault_app/             # Android application
│   ├── main.py           # Kivy-based mobile app
│   ├── buildozer.spec    # Android build config
│   └── venv/            # Python virtual environment
├── setup.sh              # Installation script
├── SECURITY.md           # Security considerations
├── CONTRIBUTING.md       # Development guidelines
└── README.md            # This file
```

## 🛠️ Installation

### Prerequisites

- **Linux System** (Ubuntu/Debian recommended)
- **Kernel Headers**: `sudo apt install linux-headers-$(uname -r)`
- **Python 3.7+**: `sudo apt install python3 python3-pip`
- **Build Tools**: `sudo apt install build-essential`
- **Camera/Webcam** for QR code scanning

### Quick Install

```bash
# Clone and setup
git clone <repository-url>
cd black_box_vault
chmod +x setup.sh
./setup.sh

# Load the kernel module
sudo insmod vault_driver.ko

# Run the guard
python3 guard.py
```

### Manual Installation

#### 1. Kernel Module

```bash
# Build the module
make

# Load the kernel module
sudo insmod vault_driver.ko

# Create device node
sudo mknod /dev/secret_vault c $(grep vault_driver /proc/devices | awk '{print $1}') 0
sudo chmod 666 /dev/secret_vault
```

#### 2. Python Dependencies

```bash
# Install required packages
pip3 install -r requirements.txt

# Or install manually
pip3 install opencv-python qrcode[pil]
```

#### 3. Android App (Optional)

```bash
cd vault_app
source venv/bin/activate
pip3 install -r requirements.txt
buildozer android debug    # Requires Android SDK/NDK
```

## 🎮 Usage

### Basic Workflow

1. **Start the Guard**:
   ```bash
   python3 guard.py
   ```

2. **Generate QR Code**:
   - Open `index.html` in a web browser, OR
   - Run the Android app, OR
   - Use any QR code generator with text: `"UNLOCK_MY_VAULT_NOW"`

3. **Authenticate**:
   - Show QR code to your webcam
   - Guard will detect and validate the code
   - Vault unlocks for 30 seconds

4. **Access Secrets**:
   ```bash
   # Write secrets (while unlocked)
   echo "my_secret_password" > /dev/secret_vault
   
   # Read secrets (while unlocked)
   cat /dev/secret_vault
   ```

### Web Interface

```bash
# Start local web server
python3 -m http.server 8000

# Open browser
# http://localhost:8000/index.html
```

### Android App

```bash
cd vault_app
source venv/bin/activate
python3 main.py
```

## 🔧 Configuration

### Security Settings

- **PIN Code**: `1337` (defined in `vault_driver.c`)
- **Secret QR Text**: `"UNLOCK_MY_VAULT_NOW"` (defined in `guard.py`)
- **Auto-Lock Timeout**: `30 seconds` (configurable in kernel module)
- **Device Path**: `/dev/secret_vault`

### Customization

Edit the following constants:
- `vault_driver.c`: `VAULT_PIN`, `MAX_SECRET`, auto-lock timer
- `guard.py`: `SECRET_QR_TEXT`, `UNLOCK_PIN`, `IOCTL_UNLOCK_CMD`

## 🧪 Testing

```bash
# Test kernel module
make && sudo insmod vault_driver.ko && dmesg | tail -10

# Test guard script (camera required)
python3 -c "import cv2, time; print('Camera test OK')"

# Test QR generation
python3 -c "import qrcode; qrcode.make('UNLOCK_MY_VAULT_NOW').save('test.png')"

# Test device access
ls -l /dev/secret_vault
```

## 🔒 Security Features

- **Kernel Isolation**: Secrets stored in kernel space, inaccessible from user space
- **Multi-Factor Auth**: Requires both PIN (kernel) and QR code (visual)
- **Auto-Lock**: Prevents indefinite access
- **Rate Limiting**: Thwarts brute-force attacks
- **Memory Protection**: Proper bounds checking and input validation
- **Secure Cleanup**: Automatic cleanup on module unload

## 🐛 Troubleshooting

### Common Issues

**Module won't load**:
```bash
# Check kernel logs
dmesg | tail -20

# Verify kernel headers
ls /lib/modules/$(uname -r)/build
```

**Camera not working**:
```bash
# Test camera access
python3 -c "import cv2; cap=cv2.VideoCapture(0); print('Camera OK' if cap.isOpened() else 'Camera failed')"
```

**Device not found**:
```bash
# Check if module is loaded
lsmod | grep vault_driver

# Recreate device node
sudo mknod /dev/secret_vault c $(grep vault_driver /proc/devices | awk '{print $1}') 0
```

**QR detection failing**:
- Ensure good lighting
- Use high-contrast QR codes
- Keep QR code stable in camera view

### Debug Mode

Enable verbose logging:
```bash
# Kernel debug
dmesg --follow

# Guard debug
python3 guard.py 2>&1 | tee guard.log
```

## 📚 Technical Details

### Kernel Module API

- **Device**: `/dev/secret_vault` (character device)
- **IOCTL**: `_IOW('v', 1, int)` for unlock command
- **Authentication**: Integer PIN 1337
- **Storage**: Circular buffer with size limits

### QR Protocol

- **Format**: Text-based QR codes
- **Secret**: `"UNLOCK_MY_VAULT_NOW"`
- **Encoding**: UTF-8
- **Error Correction**: Standard QR code levels

## 🤝 Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines and security considerations.

## 📄 License

This project is licensed under the GPL-2.0 License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Security Notice

This is a security-focused project. Please review [SECURITY.md](SECURITY.md) for important security considerations and responsible disclosure guidelines.

## 🙏 Acknowledgments

- Linux Kernel Development Community
- OpenCV Computer Vision Library
- Kivy Mobile App Framework
- QR Code Standardization

---

**⚠️ Warning**: This is a security research project. Use only for educational purposes and security testing on systems you own.