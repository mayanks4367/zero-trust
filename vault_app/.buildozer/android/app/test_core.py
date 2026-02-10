#!/usr/bin/env python3
"""
Black Box Vault - Mobile App Test Script
Tests the QR code generation functionality without Kivy UI.
"""

import qrcode
from io import BytesIO
import sys

def test_qr_generation():
    """Test QR code generation functionality."""
    print("Testing QR Code Generation...")
    
    try:
        # Test basic QR code
        data = "UNLOCK_MY_VAULT_NOW"
        
        # Generate QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.ERROR_CORRECT_L,
            box_size=10,
            border=4
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Test saving to buffer
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        
        # Get image info
        buffer.seek(0)
        size = len(buffer.getvalue())
        
        print(f"✓ QR Code generated successfully")
        print(f"✓ Data: {data}")
        print(f"✓ Image size: {size} bytes")
        print(f"✓ Image dimensions: {img.size}")
        
        # Save test file
        with open('test_qr.png', 'wb') as f:
            f.write(buffer.getvalue())
        
        print("✓ Test QR code saved as 'test_qr.png'")
        return True
        
    except Exception as e:
        print(f"✗ QR Code generation failed: {e}")
        return False

def test_dependencies():
    """Test all required dependencies."""
    print("Testing Dependencies...")
    
    # Test qrcode
    try:
        import qrcode
        print("✓ qrcode imported successfully")
    except ImportError as e:
        print(f"✗ qrcode not available: {e}")
        return False
    
    # Test PIL/Pillow
    try:
        from PIL import Image
        print("✓ PIL/Pillow imported successfully")
    except ImportError as e:
        print(f"✗ PIL/Pillow not available: {e}")
        return False
    
    # Test BytesIO
    try:
        from io import BytesIO
        print("✓ BytesIO imported successfully")
    except ImportError as e:
        print(f"✗ BytesIO not available: {e}")
        return False
    
    return True

def main():
    """Main test function."""
    print("=" * 50)
    print("Black Box Vault - Mobile App Test")
    print("=" * 50)
    print("")
    
    # Test dependencies
    if not test_dependencies():
        print("\n❌ Dependency test failed!")
        sys.exit(1)
    
    print("")
    
    # Test QR generation
    if test_qr_generation():
        print("\n🎉 All tests passed!")
        print("\n📱 Mobile app core functionality is working correctly.")
        print("📝 Kivy UI layer can be built with working QR generation.")
        print("🔍 You can now proceed with 'buildozer android debug'")
    else:
        print("\n❌ QR generation test failed!")
        sys.exit(1)
    
    print("")
    print("Next steps:")
    print("1. cd vault_app")
    print("2. source venv/bin/activate")
    print("3. buildozer android debug")

if __name__ == '__main__':
    main()