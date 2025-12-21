# Raspberry Pi Setup Guide for Deepfake Audio Detection

## Hardware Required
- Raspberry Pi (3/4/5 or Zero W)
- USB Microphone or USB sound card with microphone
- Push button
- Red LED + 220Ω resistor
- Green LED + 220Ω resistor
- Breadboard and jumper wires

## Wiring Diagram

```
Button Connection:
- One side of button → GPIO 17
- Other side of button → Ground (GND)
- Internal pull-up resistor enabled in code

Red LED (Fake):
- Long leg (Anode +) → GPIO 23
- Short leg (Cathode -) → 220Ω resistor → Ground (GND)

Green LED (Real):
- Long leg (Anode +) → GPIO 24
- Short leg (Cathode -) → 220Ω resistor → Ground (GND)

Microphone:
- Connect USB microphone to any USB port
```

## Pin Layout
```
GPIO 17 (Pin 11) ← Button
GPIO 23 (Pin 16) → Red LED (Fake)
GPIO 24 (Pin 18) → Green LED (Real)
Ground (Pin 6, 9, 14, 20, 25, 30, 34, 39) ← Button & LEDs
```

## Software Installation

### 1. Update System
```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### 2. Install Required Packages
```bash
# Install Python dependencies
sudo apt-get install -y python3-pip python3-dev libasound2-dev portaudio19-dev

# Install Python libraries
pip3 install RPi.GPIO pyaudio requests
```

### 3. Test Microphone
```bash
# List audio devices
arecord -l

# Test recording (5 seconds)
arecord -d 5 -f cd test.wav

# Play back
aplay test.wav
```

### 4. Download Client Script
```bash
# Copy raspberry_pi_client.py to your Pi
scp raspberry_pi_client.py pi@raspberrypi.local:/home/pi/
```

### 5. Configure API URL

Edit the script and change the API URL to your server's IP:
```bash
nano raspberry_pi_client.py
```

Change this line:
```python
API_URL = "http://192.168.1.100:8000/predict"  # Your API server IP
```

### 6. Test GPIO LEDs
```bash
# Test script
python3 << EOF
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.OUT)  # Red LED
GPIO.setup(24, GPIO.OUT)  # Green LED

# Blink red
GPIO.output(23, GPIO.HIGH)
time.sleep(1)
GPIO.output(23, GPIO.LOW)

# Blink green
GPIO.output(24, GPIO.HIGH)
time.sleep(1)
GPIO.output(24, GPIO.LOW)

GPIO.cleanup()
EOF
```

## Running the Client

### Manual Run
```bash
python3 raspberry_pi_client.py
```

### Run on Boot (Optional)

1. Create systemd service:
```bash
sudo nano /etc/systemd/system/deepfake-detector.service
```

2. Add this content:
```ini
[Unit]
Description=Deepfake Audio Detector
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi
ExecStart=/usr/bin/python3 /home/pi/raspberry_pi_client.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

3. Enable and start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable deepfake-detector.service
sudo systemctl start deepfake-detector.service

# Check status
sudo systemctl status deepfake-detector.service

# View logs
sudo journalctl -u deepfake-detector.service -f
```

## Usage

1. **Start the script** (if not running as service):
   ```bash
   python3 raspberry_pi_client.py
   ```

2. **Press and HOLD the button** - Recording starts
   - You'll see "🎙️ Recording..." message

3. **Release the button** - Recording stops
   - Audio is sent to API automatically
   - Wait for LED response

4. **LED Indicators**:
   - **🔴 Red LED blinks** = Fake/Deepfake audio detected
   - **🟢 Green LED blinks** = Real/Genuine audio detected
   - **Both LEDs blink rapidly** = Connection error

5. **Ready for next recording** after LED turns off

## Troubleshooting

### Microphone Not Working
```bash
# Check if mic is detected
arecord -l

# Test recording
arecord -d 3 -f cd test.wav && aplay test.wav

# Set default device
nano ~/.asoundrc
# Add:
pcm.!default {
    type hw
    card 1
}
```

### GPIO Permission Error
```bash
# Add user to gpio group
sudo usermod -a -G gpio pi

# Reboot
sudo reboot
```

### API Connection Error
```bash
# Test API connectivity
curl http://YOUR_API_IP:8000/health

# Check firewall on server
# Make sure port 8000 is open (see main README)
```

### LEDs Not Working
```bash
# Check GPIO pins with test script
python3 -c "
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.OUT)
GPIO.setup(24, GPIO.OUT)
GPIO.output(23, GPIO.HIGH)
input('Red LED should be ON. Press Enter...')
GPIO.output(23, GPIO.LOW)
GPIO.output(24, GPIO.HIGH)
input('Green LED should be ON. Press Enter...')
GPIO.cleanup()
"
```

## Customization

### Change GPIO Pins
Edit in `raspberry_pi_client.py`:
```python
BUTTON_PIN = 17      # Change to your button pin
RED_LED_PIN = 23     # Change to your red LED pin
GREEN_LED_PIN = 24   # Change to your green LED pin
```

### Change Audio Quality
```python
SAMPLE_RATE = 16000  # 16kHz (default), 44100 for CD quality
CHANNELS = 1         # 1 for mono, 2 for stereo
```

### Add Buzzer Feedback
```python
BUZZER_PIN = 25
GPIO.setup(BUZZER_PIN, GPIO.OUT)

# In control_leds function:
if prediction == "fake":
    # Beep 3 times for fake
    for _ in range(3):
        GPIO.output(BUZZER_PIN, GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(BUZZER_PIN, GPIO.LOW)
        time.sleep(0.1)
```

## Advanced Features

### Add OLED Display
Show prediction on 128x64 OLED screen:
```bash
pip3 install adafruit-circuitpython-ssd1306 pillow
```

### Add WiFi Auto-Connect
```bash
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
```

### Power Saving Mode
```bash
# Disable HDMI
sudo /usr/bin/tvservice -o

# Disable WiFi power management
sudo iw wlan0 set power_save off
```

## Performance Tips

1. **Use Raspberry Pi 4** for faster processing
2. **Use USB 3.0 microphone** for better audio quality
3. **Wired Ethernet** for more reliable connection
4. **Close unnecessary services** to save resources

## Safety & Security

1. **Change default password**: `passwd`
2. **Enable firewall**: `sudo ufw enable`
3. **Update regularly**: `sudo apt-get update && sudo apt-get upgrade`
4. **Use HTTPS** for production (add SSL to API)

## Questions?

- Check API server is running: `http://YOUR_SERVER_IP:8000/health`
- Check Pi connectivity: `ping YOUR_SERVER_IP`
- View logs: `python3 raspberry_pi_client.py` (manual mode)
