#!/usr/bin/env python3
"""
Zero-Trust Guard (Dynamic TOTP Version)
"""
import cv2
import os
import fcntl
import struct
import time
import hmac
import hashlib
import numpy as np

# --- CONFIGURATION ---
DEVICE_PATH = "/dev/secret_vault"
UNLOCK_PIN = 1337
IOCTL_UNLOCK_CMD = 0x40047601
# MUST match the key in main.py
SHARED_SECRET = b"MY_SUPER_SECRET_VAULT_KEY" 

def generate_valid_tokens():
    """Generates valid tokens for NOW and NOW-30s (to allow for delay)"""
    tokens = []
    current_block = int(time.time() // 30)
    
    # Check current window AND previous window (in case user is 1 second late)
    for block in [current_block, current_block - 1]:
        msg = struct.pack(">Q", block)
        h = hmac.new(SHARED_SECRET, msg, hashlib.sha256).hexdigest()
        tokens.append(h[:8].upper())
    return tokens

def unlock_kernel_vault():
    try:
        fd = os.open(DEVICE_PATH, os.O_RDWR)
        pin_bytes = struct.pack('I', UNLOCK_PIN)
        fcntl.ioctl(fd, IOCTL_UNLOCK_CMD, pin_bytes)
        print("\n[+] SUCCESS: Vault Unlocked!")
        os.close(fd)
        return True
    except Exception as e:
        print(f"\n[!] Unlock Error: {e}")
    return False

def start_guard():
    print("[*] Starting Dynamic TOTP Guard...")
    detector = cv2.QRCodeDetector()
    cap = cv2.VideoCapture(0)

    try:
        while True:
            ret, frame = cap.read()
            if not ret: break

            qr_data, points, _ = detector.detectAndDecode(frame)

            if qr_data:
                # --- VISUALS ---
                if points is not None:
                    if len(points.shape) == 3: points = points[0]
                    points = points.astype(int)
                    for i in range(4):
                        cv2.line(frame, tuple(points[i]), tuple(points[(i+1)%4]), (0, 255, 0), 3)

                # --- DYNAMIC VALIDATION ---
                valid_tokens = generate_valid_tokens()
                
                if qr_data in valid_tokens:
                    print(f"[+] VALID TOTP TOKEN: {qr_data}")
                    unlock_kernel_vault()
                    
                    # Success Animation
                    cv2.putText(frame, "ACCESS GRANTED", (50, 50), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.imshow('Zero-Trust Guard', frame)
                    cv2.waitKey(2000)
                    break 
                else:
                    # Print invalid only occasionally
                    print(f"[-] Invalid/Expired Token: {qr_data}")
                    time.sleep(1)

            cv2.imshow('Zero-Trust Guard', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): break
                
    except KeyboardInterrupt:
        print("\n[*] Interrupted")
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    start_guard()
