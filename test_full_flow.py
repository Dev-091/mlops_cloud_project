# test_full_flow.py
import cv2
import time
import requests
import os
from io import BytesIO

API_URL = "http://localhost:8000"

def capture_and_send_frame():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Camera not found")
        return
        
    print("🎥 Camera Preview Open. Align your hand and press 'c' to capture or 'q' to quit.")
    
    while True:
        ret, frame = cap.read()
        if not ret: break
        
        cv2.imshow("Capture Frame (Press 'c')", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('c'):
            break
        elif key == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            return

    cap.release()
    cv2.destroyAllWindows()
    
    # Encode frame to JPEG bytes
    _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
    image_bytes = BytesIO(buffer)
    
    # 1. Send to /detect
    print("📡 Sending frame to /detect...")
    resp = requests.post(f"{API_URL}/detect", files={"file": ("frame.jpg", image_bytes, "image/jpeg")})
    if resp.status_code != 200:
        print(f"❌ Detection failed: {resp.text}")
        return
    result = resp.json()
    count = result["finger_count"]
    latency = result["latency_ms"]
    print(f"✅ Detected {count} fingers | Latency: {latency}ms")
    
    # 2. Trigger EC2 launch
    if count > 0:
        print(f"🚀 Launching {count} EC2 instance(s)...")
        launch_resp = requests.post(f"{API_URL}/auto-scale", json={"count": count})
        if launch_resp.status_code == 200:
            print("✅ EC2 Launch Response:")
            print(launch_resp.json())
        else:
            print(f"❌ EC2 Launch Failed: {launch_resp.text}")
    else:
        print("⏸️ 0 fingers shown. No EC2 launch triggered.")

if __name__ == "__main__":
    print("👉 Show fingers to the camera and press Enter...")
    input()
    capture_and_send_frame()