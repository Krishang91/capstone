# 🎤 Complete Setup Summary - Hardware Button + Transcript Feature

## ✅ What's New

### 1. **Transcript Feature Added to API**
- API now transcribes audio to text using OpenAI Whisper
- Shows what was said in the audio
- Appears in web interface and JSON response

### 2. **Hardware Button Guide Created**
- Complete beginner-friendly guide
- Step-by-step wiring instructions
- Visual diagrams and troubleshooting

---

## 📦 What You Need to Buy

Since you have **Raspberry Pi** and **USB Microphone**, buy:

| Item | Quantity | Cost |
|------|----------|------|
| Push Button | 1 | $0.10 |
| Red LED | 1 | $0.10 |
| Green LED | 1 | $0.10 |
| 220Ω Resistors | 2 | $0.20 |
| Breadboard | 1 | $3.00 |
| Jumper Wires (M-F) | 20 pack | $3.00 |
| **TOTAL** | | **~$7** |

**OR** get a **Raspberry Pi Starter Kit** (~$15) with everything!

---

## 🔧 Hardware Wiring (5 minutes!)

```
Raspberry Pi         →  Component
────────────────────────────────────
Pin 11 (GPIO 17)     →  Button (one side)
Pin 14 (GND)         →  Button (other side)
                     →  Red LED short leg
                     →  Green LED short leg

Pin 16 (GPIO 23)     →  Resistor → Red LED long leg
Pin 18 (GPIO 24)     →  Resistor → Green LED long leg
```

**See [HARDWARE_SETUP_GUIDE.md](HARDWARE_SETUP_GUIDE.md) for detailed pictures!**

---

## 💻 Software Updates

### Server (Windows PC):

1. **Rebuild Docker image with Whisper**:
```cmd
cd C:\Users\loq\OneDrive\Desktop\deepfake\aasist
docker build -t iforgotmyname88/deepfake-api:latest .
```

2. **Push to Docker Hub**:
```cmd
docker push iforgotmyname88/deepfake-api:latest
```

3. **Run updated API**:
```cmd
docker run -d --gpus all --name aasist-api -p 8000:8000 iforgotmyname88/deepfake-api:latest
```

### Raspberry Pi:

1. **Install libraries**:
```bash
sudo apt-get install -y python3-pip libasound2-dev portaudio19-dev
pip3 install RPi.GPIO pyaudio requests
```

2. **Get the script**:
Transfer `raspberry_pi_client.py` to your Pi (USB, SCP, or copy-paste)

3. **Edit API URL**:
```bash
nano raspberry_pi_client.py
```
Change: `API_URL = "http://YOUR_SERVER_IP:8000/predict"`

4. **Run**:
```bash
python3 raspberry_pi_client.py
```

---

## 🎮 How It Works

### On Raspberry Pi:
1. **Press & HOLD button** → Recording starts 🎙️
2. **Speak into mic** → Audio captured
3. **Release button** → Sends to API 📤
4. **Wait 2-3 seconds** → LED response:
   - 🔴 **Red LED blinks** = FAKE audio
   - 🟢 **Green LED blinks** = REAL audio

### On Web Interface:
1. Go to: `http://YOUR_SERVER_IP:8000/web`
2. Upload audio file
3. See results:
   - Prediction: REAL or FAKE
   - Confidence score
   - **📝 Transcript: What was said**

---

## 🆕 API Response Now Includes Transcript

**Before:**
```json
{
  "filename": "test.wav",
  "prediction": "fake",
  "confidence": 0.87,
  "score": -2.45
}
```

**After (with transcript):**
```json
{
  "filename": "test.wav",
  "prediction": "fake",
  "confidence": 0.87,
  "score": -2.45,
  "transcript": "Hello, this is a test message"
}
```

---

## 📝 Files You Have

1. **[raspberry_pi_client.py](raspberry_pi_client.py)** - Button control script
2. **[HARDWARE_SETUP_GUIDE.md](HARDWARE_SETUP_GUIDE.md)** - Detailed wiring guide (⭐ START HERE)
3. **[RASPBERRY_PI_SETUP.md](RASPBERRY_PI_SETUP.md)** - Software installation
4. **[api.py](api.py)** - Updated with Whisper transcript
5. **[requirements-api.txt](requirements-api.txt)** - Updated dependencies

---

## 🧪 Quick Tests

### Test LEDs:
```bash
python3 << EOF
import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.OUT)
GPIO.setup(24, GPIO.OUT)
# Blink red
GPIO.output(23, GPIO.HIGH)
time.sleep(1)
GPIO.output(23, GPIO.LOW)
# Blink green
GPIO.output(24, GPIO.HIGH)
time.sleep(1)
GPIO.cleanup()
EOF
```

### Test Microphone:
```bash
arecord -d 3 test.wav
aplay test.wav
```

### Test API:
```bash
curl http://YOUR_SERVER_IP:8000/health
```

---

## 🔧 Common Issues

**Transcript shows "[Transcript unavailable]":**
- First run downloads Whisper model (~140MB), be patient
- Check audio has speech
- Check: `docker logs aasist-api`

**Button not responding:**
- Check GPIO 17 wiring
- Test button with multimeter

**LEDs not lighting:**
- Check LED orientation (long leg = +)
- Verify resistor connections

**Can't reach API from Pi:**
- Check firewall: `netsh advfirewall firewall show rule name="Docker API Port 8000"`
- Test: `curl http://SERVER_IP:8000/health`

---

## 🚀 Quick Commands

**Run everything:**
```bash
# Server
docker run -d --gpus all --name aasist-api -p 8000:8000 iforgotmyname88/deepfake-api:latest

# Raspberry Pi
python3 raspberry_pi_client.py
```

**Access web interface:**
```
http://YOUR_SERVER_IP:8000/web
```

---

## 🎉 Ready to Go!

1. ⚡ **Wire up hardware** (5 min) - See [HARDWARE_SETUP_GUIDE.md](HARDWARE_SETUP_GUIDE.md)
2. 💻 **Install Pi software** (5 min)
3. 🚀 **Run script** and press button!

**Press → Speak → Release → See LED! 🎤🔴🟢**
