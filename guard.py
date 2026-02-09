import cv2
import os
import fcntl
import struct
import time
from pyzbar.pyzbar import decode

# --- CONFIGURATION ---
DEVICE_PATH = "/dev/secret_vault"
UNLOCK_PIN = 1337           # Must match the C code
SECRET_QR_TEXT = "UNLOCK_MY_VAULT_NOW" # The text inside the QR code
# Calculate the IOCTL command number manually (matches _IOW('v', 1, int))
# On x86_64, 'v' (118) << 8 | 1 = ... usually 0x40047601
IOCTL_UNLOCK_CMD = 0x40047601 

def unlock_kernel_vault():
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
    except Exception as e:
        print(f"\n[!] ERROR: {e}")
    return False

def start_guard():
    print("[*] Starting Zero-Trust Guard...")
    print("[*] Waiting for QR Code...")
    
    # Open Webcam (0 is usually the default cam)
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Decode any QR codes in the frame
        decoded_objects = decode(frame)

        for obj in decoded_objects:
            qr_data = obj.data.decode("utf-8")
            
            # Draw a rectangle around the QR code (Visual Feedback)
            points = obj.polygon
            if len(points) == 4:
                pts = [(p.x, p.y) for p in points]
                for i in range(4):
                    cv2.line(frame, pts[i], pts[(i+1)%4], (0, 255, 0), 3)

            # CHECK THE KEY
            if qr_data == SECRET_QR_TEXT:
                print(f"[+] VALID KEY DETECTED: {qr_data}")
                unlock_kernel_vault()
                
                # Wait 5 seconds so we don't spam the kernel
                time.sleep(5)
            else:
                print(f"[-] Invalid Key: {qr_data}")

        # Show the video feed
        cv2.imshow('Zero-Trust Guard', frame)

        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    if not os.path.exists(DEVICE_PATH):
        print(f"[!] Error: {DEVICE_PATH} not found. Did you run 'sudo insmod vault.ko'?")
    else:
        start_guard()
