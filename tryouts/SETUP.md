# SmartSpace ITB — Setup Guide
## Arsitektur Sistem

```
[Arduino + HC-SR04 + DHT11]
          ↓ USB Serial
     [bridge.py (laptop)]
          ↓ Internet
     [Firebase Realtime DB]
          ↓ WebSocket
     [index.html (browser)]
```

---

## STEP 1 — Wiring Arduino

### Trash Bin (HC-SR04)
| HC-SR04 | Arduino |
|---------|---------|
| VCC     | 5V      |
| GND     | GND     |
| Trig    | Pin 9   |
| Echo    | Pin 10  |

Pasang sensor di TUTUP tempat sampah, menghadap ke bawah.
Ukur jarak dari sensor ke dasar tempat sampah kosong → isi ke `BIN_EMPTY_CM`.

### Temperature (DHT11)
| DHT11 | Arduino |
|-------|---------|
| VCC   | 5V      |
| GND   | GND     |
| DATA  | Pin 2   |

Pasang resistor 10kΩ antara pin DATA dan VCC (pull-up).

---

## STEP 2 — Upload Arduino Code

1. Buka `SmartSpace_Sensors.ino` di Arduino IDE
2. Install library: Tools → Manage Libraries → cari **"DHT sensor library"** by Adafruit → Install
3. Pilih board: Tools → Board → Arduino Uno
4. Pilih port: Tools → Port → (pilih COM yang muncul)
5. Upload ▶
6. Buka Serial Monitor (9600 baud) → pastikan muncul `DATA,XX,XX.X,XX.X`

---

## STEP 3 — Firebase Setup

1. Buka https://console.firebase.google.com
2. Create a project (nama bebas, misal "smartspace-itb")
3. Build → Realtime Database → Create database → Start in **test mode**
4. Catat URL database (contoh: `https://smartspace-itb-default-rtdb.firebaseio.com`)
5. Project Settings (⚙️) → Service Accounts → **Generate new private key**
6. Simpan file JSON yang didownload sebagai `firebase_key.json` di folder yang sama dengan `bridge.py`
7. Project Settings → General → Your apps → Add app → **Web (</>)**
8. Catat `apiKey` dan `projectId` → isi ke `index.html` bagian `FIREBASE_CONFIG`

---

## STEP 4 — Install & Jalankan Python Bridge

```bash
pip install pyserial firebase-admin opencv-python
```

Edit `bridge.py`:
- `SERIAL_PORT` → port Arduino kamu (cek di Arduino IDE → Tools → Port)
  - Windows: `"COM3"`, `"COM4"`, dll
  - Mac: `"/dev/cu.usbmodem..."` atau `"/dev/tty.usbserial..."`
  - Linux: `"/dev/ttyUSB0"` atau `"/dev/ttyACM0"`
- `FIREBASE_DB_URL` → URL database kamu
- `FIREBASE_KEY` → path ke file `firebase_key.json`

Jalankan:
```bash
python bridge.py
```

Kalau berhasil akan muncul:
```
✅ Firebase connected.
✅ Arduino connected on COM3
📤 Sent → Trash: 23% | Temp: 28.5°C | Hum: 65.0% | People: 0
```

---

## STEP 5 — People Counting dengan DroidCam

### DroidCam (kamera HP)
1. Install DroidCam di HP (iOS/Android) dan DroidCam Client di laptop
2. Hubungkan ke WiFi yang sama
3. Di `bridge.py`: set `USE_DROIDCAM = True`
4. Isi `DROIDCAM_URL` dengan IP yang muncul di app DroidCam HP
   (contoh: `"http://192.168.1.5:4747/video"`)
---

## STEP 6 — Deploy Website

Karena index.html adalah static file, bisa langsung:
- **GitHub Pages**: push ke repo → Settings → Pages → deploy dari branch main
- **Netlify**: drag & drop folder ke netlify.com/drop
- **Lokal**: buka index.html langsung di browser (Firebase tetap realtime)

---

## Troubleshooting

| Masalah | Solusi |
|---------|--------|
| Serial port not found | Cek Device Manager (Windows) / `ls /dev/tty*` (Mac/Linux) |
| DHT11 selalu ERR | Cek resistor pull-up 10kΩ, coba ganti pin |
| Firebase permission denied | Pastikan Rules = `".read": true, ".write": true` (test mode) |
| Website tidak update | Buka DevTools → Console, cek error Firebase config |
| DroidCam gagal connect | Pastikan HP & laptop di WiFi yang sama, cek IP di app DroidCam |
