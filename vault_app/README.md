# 📱 Black Box Vault Mobile App - Complete Build Guide

This guide provides step-by-step instructions for building and deploying the Black Box Vault Android application.

## 🎯 Quick Start

```bash
cd vault_app
chmod +x build.sh
./build.sh build
```

## 🔧 Prerequisites Installation

### System Requirements
```bash
# Install essential build tools
sudo apt update
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    build-essential \
    cmake \
    git

# For Android SDK support (optional)
sudo apt install -y \
    default-jdk \
    wget
```

### Verification
```bash
# Check Python version (must be 3.7+)
python3 --version

# Check pip
pip3 --version

# Verify installations
python3 -c "import kivy" 2>/dev/null && echo "✓ Kivy available" || echo "✗ Kivy missing"
python3 -c "import qrcode" 2>/dev/null && echo "✓ QRCode available" || echo "✗ QRCode missing"
```

## 🏗️ Build Process

### Step 1: Environment Setup
```bash
cd vault_app

# The build script handles this automatically
./build.sh clean
```

### Step 2: Local Testing
```bash
# Test the app locally first
./build.sh test
```

### Step 3: Android Build
```bash
# Build for Android APK
./build.sh build
```

### Step 4: Deploy to Device
```bash
# Install on connected Android device
./build.sh deploy
```

## 📱 APK Location

After successful build, the APK will be located at:
```
bin/BlackBoxVault-1.0.0-debug.apk
```

## 🔍 Manual Installation

If the build script fails, you can manually install dependencies:

### Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Build Commands
```bash
# Build using buildozer directly
source venv/bin/activate
buildozer android debug
```

## 🐛 Common Issues & Solutions

### 1. CMake Missing
**Error**: `sh.CommandNotFound: cmake`
**Solution**:
```bash
sudo apt install -y cmake build-essential
```

### 2. Kivy Import Errors
**Error**: `ImportError: No module named 'kivy'`
**Solution**:
```bash
# Install Kivy properly
pip install kivy>=2.2.0
```

### 3. Buildozer Permission Errors
**Error**: Permission denied accessing Android SDK
**Solution**:
```bash
# Set proper permissions
sudo chown -R $USER:$USER ~/.buildozer/
chmod -R 755 ~/.buildozer/
```

### 4. ADB Connection Issues
**Error**: "No Android device connected"
**Solution**:
```bash
# Enable USB debugging on Android
# Check device connection
adb devices
# Restart ADB server
adb kill-server && adb start-server
```

### 5. QR Code Generation Issues
**Error**: QR code not displaying
**Solution**:
- Check qrcode library: `pip show qrcode`
- Test locally: `python3 -c "import qrcode; print(qrcode.make('test'))"`
- Verify image size and format

## 📋 File Structure

```
vault_app/
├── main.py                 # Main application file
├── buildozer.spec          # Build configuration
├── build.sh               # Build automation script
├── requirements.txt         # Python dependencies
├── venv/                  # Virtual environment
└── bin/                   # Build output (APK location)
    ├── BlackBoxVault-1.0.0-debug.apk
    └── BlackBoxVault-1.0.0-debug.apk.md5
```

## 🧪 Testing

### Unit Testing
```bash
# Test individual components
python3 -c "
import qrcode, kivy
from kivy.uix.image import Image
print('✓ All imports working')
"
```

### Integration Testing
```bash
# Test QR code generation
python3 -c "
import qrcode
img = qrcode.make('TEST_SECRET')
img.save('test_qr.png')
print('✓ QR code generation test passed')
"
```

## 📊 APK Information

After successful build, verify APK properties:

```bash
# Check APK info
aapt dump badging bin/BlackBoxVault-1.0.0-debug.apk

# Check file size
ls -lh bin/BlackBoxVault-1.0.0-debug.apk

# Verify package name
unzip -l bin/BlackBoxVault-1.0.0-debug.apk
```

## 🔐 Security Considerations

### App Signing (Production)
- For production builds, create a keystore:
```bash
keytool -genkey -v -keystore blackboxvault.keystore -alias blackboxvault
```

### Permission Management
- Only request necessary permissions
- Current permissions: `android.permission.CAMERA`
- Consider privacy impact

## 📱 Device Requirements

- Android API Level: 24+ (Android 7.0+)
- Screen: Portrait orientation preferred
- Camera: Required for QR code display
- Storage: Optional (for debugging)

## 🚀 Deployment Options

### 1. Direct Installation
```bash
# Transfer APK to device and install
adb install bin/BlackBoxVault-1.0.0-debug.apk
```

### 2. Debug Testing
```bash
# Install with debugging enabled
adb install -d bin/BlackBoxVault-1.0.0-debug.apk

# Monitor logs
adb logcat | grep "blackboxvault"
```

### 3. Performance Profiling
```bash
# Monitor performance during testing
adb shell dumpsys meminfo org.blackboxvault
adb shell dumpsys cpuinfo | grep blackboxvault
```

## 📚 Advanced Configuration

### Custom Icons
Create `icon.png` in vault_app directory:
- Size: 512x512 pixels
- Format: PNG
- Design: Simple black box with lock symbol

### Custom Features
The app supports:
- ✅ QR code generation
- ✅ Real-time status updates
- ✅ Error handling and recovery
- ✅ Mobile-friendly responsive design
- ✅ Dark/light theme support
- ✅ App lifecycle management

## 🔧 Troubleshooting

### Clean Build
```bash
# Remove all build artifacts
./build.sh clean

# Or manual clean
rm -rf bin/ .buildozer/ __pycache__/
```

### Dependency Issues
```bash
# Reinstall all dependencies
rm -rf venv/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### ADB Issues
```bash
# Restart ADB completely
adb kill-server
adb start-server
adb devices

# Check USB debugging on Android device
# Settings > Developer Options > USB Debugging
```

---

**🎉 Success Criteria**: Your app is ready when:
- ✅ All dependencies installed without errors
- ✅ Local test runs successfully
- ✅ Buildozer completes without critical errors
- ✅ APK generated and can be installed
- ✅ QR code displays correctly on device

For additional support, check the main project documentation or create an issue on GitHub.