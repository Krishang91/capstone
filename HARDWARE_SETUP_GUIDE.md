# 🔧 Complete Hardware Setup Guide (Beginner-Friendly)

## What You Have:
- ✅ Raspberry Pi
- ✅ USB Microphone
- ✅ Push Button
- ✅ Red LED
- ✅ Green LED
- ✅ 2x 220Ω Resistors
- ✅ Breadboard
- ✅ Jumper Wires

---

## Step 1: Understand Raspberry Pi GPIO Pins

Your Raspberry Pi has 40 pins. Here's what you need to know:

```
      3V3  (1) (2)  5V
    GPIO2  (3) (4)  5V
    GPIO3  (5) (6)  GND     ← We'll use this GROUND
    GPIO4  (7) (8)  GPIO14
      GND  (9) (10) GPIO15
   GPIO17 (11) (12) GPIO18  ← GPIO 17 for BUTTON
   GPIO27 (13) (14) GND     ← We'll use this GROUND
   GPIO22 (15) (16) GPIO23  ← GPIO 23 for RED LED
      3V3 (17) (18) GPIO24  ← GPIO 24 for GREEN LED
   GPIO10 (19) (20) GND     ← We'll use this GROUND
    ...
```

**We will use:**
- **GPIO 17** (Physical Pin 11) → Button
- **GPIO 23** (Physical Pin 16) → Red LED
- **GPIO 24** (Physical Pin 18) → Green LED
- **GND** (Physical Pin 6, 14, or 20) → Ground for button and LEDs

---

## Step 2: Setup Breadboard & Ground Rail

### Understanding Breadboard:
```
     a b c d e   f g h i j
   +-+-+-+-+-+ +-+-+-+-+-+
 1 | | | | | | | | | | | |  ← Rows: Holes a-e connected, f-j connected
 2 | | | | | | | | | | | |
 3 | | | | | | | | | | | |
   ...

Power Rails (VERY IMPORTANT - sides of breadboard):
+ + + + + + + + +  ← All + connected vertically (positive rail)
- - - - - - - - -  ← All - connected vertically (GROUND rail) ⭐
```

### ⭐ IMPORTANT: How to Share Ground (Pin 14)

Since we need to connect 3 things to ground (button, red LED, green LED), we'll use the **breadboard's ground rail (-)**:

**Setup:**
1. Connect **ONE wire** from Pi **Pin 14 (GND)** to the breadboard's **ground rail (-)** (the blue/black line on the side)
2. Now all 3 components can share this ground by connecting to the **ground rail**

**This is how we share Pin 14!** The ground rail acts like a "splitter" - one connection from Pi, multiple components can use it.

---

## Step 3: Place Button Correctly

### Understanding the Button:

Most tactile buttons have **4 pins** arranged like this:

```
View from top:
  ┌─────────┐
  │  ●   ●  │  ← Pin 1    Pin 2
  │         │
  │  [  ]   │  ← Button press area
  │         │
  │  ●   ●  │  ← Pin 3    Pin 4
  └─────────┘

Side view:
Pins 1&2 are ALWAYS connected
Pins 3&4 are ALWAYS connected
When pressed: 1&2 connect to 3&4
```

### How to Place on Breadboard:

**If button is TOO SMALL to span the gap, that's OK!** Place it on ONE SIDE:

```
Breadboard (ONE SIDE ONLY):
        a b c d e
Row 1:  [●] [●]      ← Pins 1 & 2 (top row)
Row 2:  [ ] [ ]
Row 3:  [●] [●]      ← Pins 3 & 4 (bottom row)
```

**Steps:**
1. Place button on LEFT side of breadboard (columns a-e)
2. Two pins in row 1, two pins in row 3
3. We'll use **diagonal pins** (opposite corners)
   - Top-left pin (row 1, column a)
   - Bottom-right pin (row 3, column b or c)

**Why this works:** When you press the button, the diagonal pins connect!

**Alternative if button DOES span the gap:**
```
        a b c d e | f g h i j
Row 1:  [●]       |       [●]    ← Spans across
Row 3:  [●]       |       [●]
```

---

## Step 4: Connect Button

### What You Need:
- Button (already placed on breadboard)
- 2x Jumper wires (Male-to-Female)

### Wiring Steps:

1. **Connect ground rail first** (so we can share it):
   - Take a Male-to-Female jumper wire
   - Female end → Raspberry Pi **Pin 14 (GND)**
   - Male end → Breadboard **ground rail (-)** (the vertical line marked with blue/black)

2. **Connect button to GPIO 17**:
   - Take another jumper wire
   - One end → Raspberry Pi **Pin 11 (GPIO 17)**
   - Other end → **One button pin** (for example: row 1, column a - the top-left pin)

3. **Connect button to ground rail**:
   - Take another jumper wire (or use a short wire on breadboard)
   - One end → **Opposite diagonal button pin** (for example: row 3, column b - the bottom-right pin)
   - Other end → Breadboard **ground rail (-)**

**Visual (Small Button on One Side):**
```
Raspberry Pi                 Breadboard (LEFT SIDE)
                                   a   b   c   d   e
Pin 14 (GND)    ──────────→ Ground Rail (-)
                                   ↑
Pin 11 (GPIO17) ─────────→ Row 1: [●] [●]  ← Button top pins
                            Row 3: [●] [●]  ← Button bottom pins
                                       ↓
                              Connect to Ground Rail (-)
```

**Important:** Use **diagonal pins** (opposite corners of the button) - one connects to GPIO 17, the other to ground.

**Test:** Button is ready!

---

## Step 5: Connect Red LED (For "Fake" Detection)

### What You Need:
- 1x Red LED
- 1x 220Ω resistor
- 2x Jumper wires (or 1 wire if using breadboard jumper)

### Understanding LED:
```
    Long leg (+) ← Connect to GPIO (through resistor)
    Short leg (-) ← Connect to Ground
```

### Steps:

1. **Place Red LED on breadboard** (use rows 5-6 for example):
   - **Long leg (+)** → Insert into **row 5, column 'c'**
   - **Short leg (-)** → Insert into **row 6, column 'c'**

2. **Place resistor**:
   - One leg → Same row as LED's long leg: **row 5, column 'e'**
   - Other leg → Empty row: **row 7, column 'e'**

3. **Connect resistor to GPIO 23**:
   - Take a jumper wire
   - One end → Raspberry Pi **Pin 16 (GPIO 23)**
   - Other end → **row 7** (where resistor's other leg is)

4. **Connect LED short leg to ground rail**:
   - Take a short jumper wire
   - One end → **row 6** (LED's short leg)
   - Other end → **Ground rail (-)** (shares the same ground as button!)

**Visual:**
```
Raspberry Pi                      Breadboard
Pin 16 (GPIO23) ────────→ Row 7 ── Resistor ── Row 5 ── Red LED (+)
                                                Row 6 ── Red LED (-) ──→ Ground Rail (-)
                                                                            ↑
                                                              (Shared with button & Pi Pin 14)
```

**Notice:** LED short leg connects to the **same ground rail** as button - this is how we share Pin 14!

---

## Step 6: Connect Green LED (For "Real" Detection)

### Same process as Red LED, just different rows:

1. **Place Green LED on breadboard** (use rows 9-10):
   - **Long leg (+)** → Insert into **row 9, column 'c'**
   - **Short leg (-)** → Insert into **row 10, column 'c'**

2. **Place resistor**:
   - One leg → Same row as LED's long leg: **row 9, column 'e'**
   - Other leg → Empty row: **row 11, column 'e'**

3. **Connect to GPIO 24**:
   - Wire from Raspberry Pi **Pin 18 (GPIO 24)** → **row 11**

4. **Connect to ground rail**:
   - Short wire from **row 10** → **Ground rail (-)** (same ground rail again!)

**Visual:**
```
Raspberry Pi                      Breadboard
Pin 18 (GPIO24) ────────→ Row 11 ── Resistor ── Row 9 ── Green LED (+)
                                                  Row 10 ── Green LED (-) ──→ Ground Rail (-)
                                                                                 ↑
                                                                   (Shared with button, red LED, Pi Pin 14)
```

---

## Step 7: Connect USB Microphone

**Super Easy!**
1. Plug USB microphone into any USB port on Raspberry Pi
2. That's it! 🎤

---

## Step 8: COMPLETE WIRING DIAGRAM

### Final Connection Summary:

**From Raspberry Pi:**
```
Pin 11 (GPIO 17) → Button top pin
Pin 14 (GND)     → Ground rail (-) on breadboard ⭐ SHARED!
Pin 16 (GPIO 23) → Red LED circuit
Pin 18 (GPIO 24) → Green LED circuit
```

**On Breadboard:**
```
GROUND RAIL (-)  ← Pin 14 connects here (ONE wire from Pi)
   ↓
   ├──→ Button bottom pin (row 3)
   ├──→ Red LED short leg (row 6)
   └──→ Green LED short leg (row 10)

Row 1:  Button top pin ←───────── Pin 11 (GPIO 17)
Row 3:  Button bottom pin ───→ Ground Rail

Row 5:  Red LED long leg (+) ← Resistor ← Row 7 ←──── Pin 16 (GPIO 23)
Row 6:  Red LED short leg (-) ───────────→ Ground Rail

Row 9:  Green LED long leg (+) ← Resistor ← Row 11 ←── Pin 18 (GPIO 24)
Row 10: Green LED short leg (-) ─────────→ Ground Rail
```

### Complete Visual (Side View):

```
RASPBERRY PI                    BREADBOARD
                          Ground Rail (-)
Pin 14 (GND) ══════════════════╪═════════
                               ║
Pin 11 (GPIO17) ───┐           ║
                   ↓           ↓
              Row 1: [Button Top Pin]
              Row 3: [Button Bot Pin]─────┘

Pin 16 (GPIO23) ───┐
                   ↓
              Row 7: [Resistor]
              Row 5: [Resistor]
              Row 5: [Red LED Long +]
              Row 6: [Red LED Short -]─────┘

Pin 18 (GPIO24) ───┐
                   ↓
              Row 11: [Resistor]
              Row 9:  [Resistor]
              Row 9:  [Green LED Long +]
              Row 10: [Green LED Short -]──┘
```

**KEY POINT:** Only **ONE wire** from Pi Pin 14 goes to the ground rail, then all 3 components (button, red LED, green LED) connect their negative sides to this same ground rail. This is how you share Pin 14!

---

## Step 9: Double-Check Your Wiring

### Checklist:
- [ ] Button straddles middle gap on breadboard
- [ ] Button top pin connects to GPIO 17
- [ ] Button bottom pin connects to ground rail
- [ ] Ground rail has ONE wire from Pi Pin 14
- [ ] Red LED long leg goes through resistor to GPIO 23
- [ ] Red LED short leg connects to ground rail
- [ ] Green LED long leg goes through resistor to GPIO 24
- [ ] Green LED short leg connects to ground rail
- [ ] USB microphone plugged in

### Wire Count:
- Total wires from Pi to breadboard: **4 wires**
  1. Pin 11 → Button
  2. Pin 14 → Ground rail
  3. Pin 16 → Red LED resistor
  4. Pin 18 → Green LED resistor

- Short jumper wires on breadboard: **3 wires**
  1. Button → Ground rail
  2. Red LED → Ground rail
  3. Green LED → Ground rail

**Total: 7 wires + components**

**Visual:**
```
Raspberry Pi                      Breadboard
Pin 18 (GPIO24) ----Wire---→ Resistor---→ Green LED (long leg +)
Pin 14 (GND)    ----Wire---→ Green LED (short leg -)
```

---

## Step 6: Connect USB Microphone

**Super Easy!**
1. Plug USB microphone into any USB port on Raspberry Pi
2. That's it! 🎤

---

## Step 7: Complete Wiring Summary

```
RASPBERRY PI          COMPONENT
────────────────────────────────────
Pin 11 (GPIO 17) →→→  Button (one side)
Pin 14 (GND)     →→→  Button (other side)
                 →→→  Red LED short leg
                 →→→  Green LED short leg

Pin 16 (GPIO 23) →→→  220Ω Resistor → Red LED long leg
Pin 18 (GPIO 24) →→→  220Ω Resistor → Green LED long leg

USB Port         →→→  USB Microphone
```

---

## Step 8: Visual Diagram (Text Version)

```
                    RASPBERRY PI
                 ╔════════════════╗
                 ║  ○ ○ ○ ○ ○    ║
  To Button ←────║ 11           ║
  To GND ←───────║ 14           ║
  To Red LED ←───║ 16           ║
  To Green LED ←─║ 18           ║
                 ║               ║
                 ╚════════════════╝
                        │
                    USB Mic

              BREADBOARD
     ┌──────────────────────┐
     │                      │
     │  [Button]            │  ← Row 1-3
     │     │  │             │
     │   GPIO17  GND        │
     │                      │
     │  [Resistor]─[Red LED]│  ← Row 5-7
     │     │         │      │
     │   GPIO23     GND     │
     │                      │
     │  [Resistor]─[GrnLED] │  ← Row 8-10
     │     │         │      │
     │   GPIO24     GND     │
     └──────────────────────┘
```

---

## Step 9: Software Setup on Raspberry Pi

### 1. Power on Raspberry Pi and open Terminal

### 2. Install required software:
```bash
sudo apt-get update
sudo apt-get install -y python3-pip libasound2-dev portaudio19-dev
pip3 install RPi.GPIO pyaudio requests
```

### 3. Download the script:
```bash
# Create a folder
mkdir ~/deepfake-detector
cd ~/deepfake-detector

# Download script (or copy from your computer)
# Use: scp, wget, or just copy-paste into nano
nano raspberry_pi_client.py
```

### 4. Edit API URL in the script:
Find this line and change IP to your server:
```python
API_URL = "http://192.168.1.100:8000/predict"  # Change this!
```

To find your server IP:
- On Windows: Open cmd → type `ipconfig` → look for IPv4 Address
- Example: `http://172.16.41.40:8000/predict`

### 5. Run the script:
```bash
python3 raspberry_pi_client.py
```

---

## Step 10: Testing!

### Test 1: LEDs Work
When you run the script, you should see:
```
🎤 Deepfake Audio Detection - Raspberry Pi Client
================================================
API: http://172.16.41.40:8000/predict
Button: GPIO 17
Red LED (Fake): GPIO 23
Green LED (Real): GPIO 24

📌 Press and HOLD button to record audio
```

### Test 2: Button Works
1. **Press and HOLD** the button
2. You should see: `🎙️ Recording...`
3. **Speak into microphone** (say something for 2-3 seconds)
4. **Release button**
5. You should see: `⏹️ Recording stopped` and `📤 Sending to API...`

### Test 3: LED Response
Wait a few seconds, then:
- If audio is **FAKE**: 🔴 Red LED will blink 3 times and stay on
- If audio is **REAL**: 🟢 Green LED will blink 3 times and stay on

---

## Troubleshooting

### Button doesn't respond
- Check wiring: GPIO 17 → Button → GND
- Try pressing button firmly

### LEDs don't light up
- Check LED orientation (long leg = positive)
- Make sure resistor is connected
- Test with this command:
```bash
python3 << EOF
import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.OUT)
GPIO.output(23, GPIO.HIGH)
print("Red LED should be ON")
time.sleep(3)
GPIO.cleanup()
EOF
```

### Microphone not working
```bash
# List audio devices
arecord -l

# Test recording
arecord -d 3 test.wav
aplay test.wav
```

### API connection error
- Check API is running on server
- Check firewall allows port 8000
- Test with: `curl http://YOUR_SERVER_IP:8000/health`

---

## Quick Reference Card

**Press and HOLD button** → Records audio  
**Release button** → Sends to API  
**🔴 Red LED** → Fake audio detected  
**🟢 Green LED** → Real audio detected  
**Both blink** → Connection error  

**GPIO Pins:**
- GPIO 17 = Button
- GPIO 23 = Red LED (Fake)
- GPIO 24 = Green LED (Real)
- GND = Ground (shared)

---

## Done! 🎉

Your hardware is now complete! Press the button, speak, release, and watch the LEDs! 🚀
