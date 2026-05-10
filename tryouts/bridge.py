import serial
import time
import json
import threading
import sys

SERIAL_PORT   = "COM3"         
BAUD_RATE     = 9600
FIREBASE_DB_URL = "https://smartspace-itb-default-rtdb.asia-southeast1.firebasedatabase.app"
FIREBASE_KEY  = "firebase_key.json"  

USE_DROIDCAM  = True   
DROIDCAM_URL  = "http://192.168.1.X:4747/video"  

import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate(FIREBASE_KEY)
firebase_admin.initialize_app(cred, {"databaseURL": FIREBASE_DB_URL})
ref = db.reference("/smartspace")
print("✅ Firebase connected.")

people_count = 0

def run_people_counter():
    global people_count
    import cv2
    hog = cv2.HOGDescriptor()
    hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
    cap = cv2.VideoCapture(DROIDCAM_URL)
    print("📷 DroidCam people counter started.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠️  DroidCam frame lost, retrying...")
            time.sleep(2)
            continue
        # Resize for faster processing
        small = cv2.resize(frame, (640, 360))
        boxes, _ = hog.detectMultiScale(small, winStride=(8, 8), padding=(4, 4), scale=1.05)
        people_count = len(boxes)
        for (x, y, w, h) in boxes:
            cv2.rectangle(small, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.imshow("SmartSpace - People Counter", small)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

# --- Main Arduino reader loop ---
def run_arduino_bridge():
    global people_count
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=3)
        print(f"✅ Arduino connected on {SERIAL_PORT}")
    except serial.SerialException as e:
        print(f"❌ Could not open serial port {SERIAL_PORT}: {e}")
        print("   Check your port! On Mac/Linux run: ls /dev/tty*")
        print("   On Windows, check Device Manager for COM ports.")
        sys.exit(1)

    time.sleep(2)  # wait for Arduino to reset after connection

    while True:
        try:
            line = ser.readline().decode("utf-8").strip()
            if not line or not line.startswith("DATA,"):
                continue

            parts = line.split(",")
            if len(parts) != 4:
                continue

            fill_percent = int(parts[1])
            temp_raw     = parts[2]
            hum_raw      = parts[3]

            temperature = float(temp_raw) if temp_raw != "ERR" else None
            humidity    = float(hum_raw)  if hum_raw  != "ERR" else None

            payload = {
                "trash": {
                    "fill_percent": fill_percent,
                    "status": "penuh" if fill_percent > 75 else "aman",
                    "updated_at": int(time.time())
                },
                "environment": {
                    "temperature_c": temperature,
                    "humidity_pct":  humidity,
                    "updated_at":    int(time.time())
                },
                "people": {
                    "count":      people_count,
                    "updated_at": int(time.time())
                }
            }

            ref.update(payload)

            # Pretty print to terminal
            temp_str = f"{temperature}°C" if temperature else "ERR"
            hum_str  = f"{humidity}%"    if humidity    else "ERR"
            print(f"📤 Sent → Trash: {fill_percent}% | Temp: {temp_str} | Hum: {hum_str} | People: {people_count}")

        except (ValueError, UnicodeDecodeError) as e:
            print(f"Parse error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
            time.sleep(1)

# Start
if __name__ == "__main__":
    if USE_DROIDCAM:
        cam_thread = threading.Thread(target=run_people_counter, daemon=True)
        cam_thread.start()

    run_arduino_bridge()
