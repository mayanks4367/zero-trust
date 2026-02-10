#!/usr/bin/env python3
"""
Zero-Trust Guard Script

This script implements a QR code-based authentication system for the kernel vault.

Components:
1. Eyes: Webcam monitoring using OpenCV
2. Brain: QR code decoding and validation  
3. Hand: Kernel communication via IOCTL
4. Safety: Rate limiting to prevent kernel spam

Requirements: opencv-python, Python 3.7+
Usage: python3 guard.py (may require sudo for device access)
"""

import cv2
import os
import fcntl
import struct
import time

# --- CONFIGURATION ---
DEVICE_PATH = "/dev/secret_vault"
UNLOCK_PIN = 1337           # Must match the C code
SECRET_QR_TEXT = "UNLOCK_MY_VAULT_NOW" # The text inside the QR code
# Calculate the IOCTL command number manually (matches _IOW('v', 1, int))
# On x86_64, 'v' (118) << 8 | 1 = ... usually 0x40047601
IOCTL_UNLOCK_CMD = 0x40047601 

def unlock_kernel_vault():
    """Hand: Kernel Communication via IOCTL"""
    try:
        # 1. Open the device
        fd = os.open(DEVICE_PATH, os.O_RDWR)
        
        # 2. Pack the PIN into bytes
        pin_bytes = struct.pack('I', UNLOCK_PIN)
        
        # 3. Send the IOCTL command
        fcntl.ioctl(fd, IOCTL_UNLOCK_CMD, pin_bytes)
        
        print("\n[+] SUCCESS: Vault Unlocked for 30 seconds!")
        os.close(fd)
        return True
    except PermissionError:
        print("\n[!] ERROR: Run with sudo!")
    except OSError as e:
        if e.errno == 19:  # No such device
            print("\n[!] ERROR: Device not found. Kernel module loaded?")
        else:
            print(f"\n[!] Device error: {e}")
    except Exception as e:
        print(f"\n[!] ERROR: {e}")
    return False

def decode_qr_opencv(frame):
    """Brain: QR Code Decoding using OpenCV's built-in detector"""
    try:
        # Initialize QR code detector
        detector = cv2.QRCodeDetector()
        
        # Detect and decode
        data, points, _ = detector.detectAndDecode(frame)
        
        if data:
            return data, points
        return None, None
    except Exception as e:
        print(f"QR detection error: {e}")
        return None, None

def start_guard():
    """Eyes: Webcam Monitoring"""
    print("[*] Starting Zero-Trust Guard...")
    print("[*] Waiting for QR Code...")
    
    # Open Webcam (0 is usually the default cam)
    cap = cv2.VideoCapture(0)
    
    # Check if camera opened successfully
    if not cap.isOpened():
        print("[!] ERROR: Could not open camera")
        print("[!] Trying alternative camera indices...")
        
        # Try other camera indices
        for i in range(1, 5):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                print(f"[+] Camera {i} opened successfully")
                break
        else:
            print("[!] ERROR: Could not open any camera")
            return

    print("[+] Camera opened successfully")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("[!] ERROR: Could not read frame")
                break

            # Decode any QR codes in the frame using OpenCV
            qr_data, points = decode_qr_opencv(frame)

            if qr_data and points is not None:
                # Draw a rectangle around the QR code (Visual Feedback)
                points = points.astype(int)
                for i in range(len(points)):
                    cv2.line(frame, tuple(points[i]), tuple(points[(i+1) % len(points)]), (0, 255, 0), 3)

                # CHECK THE KEY
                if qr_data == SECRET_QR_TEXT:
                    print(f"[+] VALID KEY DETECTED: {qr_data}")
                    unlock_kernel_vault()
                    
                    # Wait 5 seconds so we don't spam the kernel (Safety: Rate Limiting)
                    print("[*] Rate limiting: Waiting 5 seconds...")
                    time.sleep(5)
                else:
                    print(f"[-] Invalid Key: {qr_data}")

            # Show the video feed
            cv2.imshow('Zero-Trust Guard', frame)

            # Press 'q' to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("\n[*] Interrupted by user")
    finally:
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        print("[*] Guard stopped")

if __name__ == "__main__":
    # Check if device exists
    if not os.path.exists(DEVICE_PATH):
        print(f"[!] Error: {DEVICE_PATH} not found.")
        print("[!] Did you run 'sudo insmod vault_driver.ko'?")
        print("[!] Or create the device node with:")
        print(f"[!] sudo mknod {DEVICE_PATH} c <major> <minor>")
    else:
        # Check if running with appropriate permissions for device access
        try:
            test_fd = os.open(DEVICE_PATH, os.O_RDONLY)
            os.close(test_fd)
            print(f"[+] Device {DEVICE_PATH} accessible")
        except PermissionError:
            print(f"[!] Warning: {DEVICE_PATH} not accessible. May need sudo or device permissions.")
        
        start_guard()