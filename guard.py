#!/usr/bin/env python3
"""
Zero-Trust Guard Script (FIXED VERSION)

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
import numpy as np

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

def start_guard():
    """Eyes: Webcam Monitoring"""
    print("[*] Starting Zero-Trust Guard...")
    print("[*] Waiting for QR Code...")
    
    # Initialize the detector once (better performance)
    detector = cv2.QRCodeDetector()

    # Open Webcam (0 is usually the default cam)
    cap = cv2.VideoCapture(0)
    
    # Check if camera opened successfully
    if not cap.isOpened():
        print("[!] ERROR: Could not open camera")
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

            # --- BRAIN: Detect and Decode ---
            qr_data, points, _ = detector.detectAndDecode(frame)

            if qr_data:
                # --- VISUALS: Draw the Green Box ---
                if points is not None:
                    # FIX: OpenCV returns points as [[[x1,y1], [x2,y2]...]] (Shape: 1,4,2)
                    # We need to unwrap the first layer to get [[x1,y1]...] (Shape: 4,2)
                    if len(points.shape) == 3:
                        points = points[0]
                    
                    # Convert to integer for drawing
                    points = points.astype(int)
                    
                    # Draw lines between corners
                    for i in range(4):
                        pt1 = tuple(points[i])
                        pt2 = tuple(points[(i+1) % 4])
                        cv2.line(frame, pt1, pt2, (0, 255, 0), 3)

                # --- SECURITY CHECK ---
                if qr_data == SECRET_QR_TEXT:
                    print(f"[+] VALID KEY DETECTED: {qr_data}")
                    unlock_kernel_vault()
    
                    print("[*] MISSION SUCCESS: Vault Unlocked.")
                    print("[*] Closing Guard automatically...")
    
                    # Visual feedback before closing (Green Box)
                    cv2.imshow('Zero-Trust Guard', frame) 
                    cv2.waitKey(2000) # Show success for 2 seconds
    
                    break 
                else:
                    # Only print invalid keys once per second to avoid spam
                    print(f"[-] Invalid Key: {qr_data}")
                    time.sleep(1)

            # Show the video feed
            cv2.imshow('Zero-Trust Guard', frame)

            # Press 'q' to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("\n[*] Interrupted by user")
    except Exception as e:
        print(f"\n[!] Unexpected Error: {e}")
    finally:
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        print("[*] Guard stopped")

if __name__ == "__main__":
    # Check if device exists
    if not os.path.exists(DEVICE_PATH):
        print(f"[!] Error: {DEVICE_PATH} not found.")
        print("[!] Did you run 'sudo insmod vault.ko'?")
    else:
        # Check permissions
        try:
            # Try to open simply to check permissions
            # Note: We use os.open just to verify access, then close immediately
            fd = os.open(DEVICE_PATH, os.O_RDONLY)
            os.close(fd)
            print(f"[+] Device {DEVICE_PATH} accessible")
            start_guard()
        except PermissionError:
            print(f"[!] Warning: {DEVICE_PATH} not accessible.")
            print(f"[!] FIX: Run 'sudo chmod 666 {DEVICE_PATH}'")
