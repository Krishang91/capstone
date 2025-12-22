# 🎯 Quick Wiring Reference

## How to Share Pin 14 (Ground)

### ⭐ EASIER METHOD: Use Multiple Ground Pins!

**The Raspberry Pi has MANY ground pins - you don't need to share one!**

Available Ground Pins:
- Pin 6 (GND)
- Pin 9 (GND)
- Pin 14 (GND)
- Pin 20 (GND)
- Pin 25 (GND)
- Pin 30 (GND)
- Pin 34 (GND)
- Pin 39 (GND)

**Simple Solution:**
```
Pin 14 (GND) → Button
Pin 20 (GND) → Red LED
Pin 25 (GND) → Green LED
```

### Alternative: Use Breadboard Ground Rail (If you prefer)

If you want to use only one ground pin:

```
╔═══════════════════════════════════════════════════════════╗
║  RASPBERRY PI                                             ║
║                                                           ║
║  Pin 11 (GPIO 17) ─────────────┐                        ║
║  Pin 14 (GND)     ─────────────┼─────┐                  ║
║  Pin 16 (GPIO 23) ─────────────┼─────┼───┐              ║
║  Pin 18 (GPIO 24) ─────────────┼─────┼───┼───┐          ║
╚════════════════════════════════╪═════╪═══╪═══╪══════════╝
                                 ↓     ↓   ↓   ↓
          ┌──────────────────────────────────────────────┐
          │  BREADBOARD                                  │
          │                                              │
          │  GROUND RAIL (-)  ←──────────────┘   │   │  │
          │      ║                                │   │  │
          │      ╠════════════════════════════════╝   │  │
          │      ║                                    │  │
          │  Row 1: [Button Top]  ←────────────────┘  │  │
          │  Row 3: [Button Bot] ──→ Ground Rail      │  │
          │                                            │  │
          │  Row 7: Wire from GPIO23 ←────────────────┘  │
          │  Row 5: [Resistor] ─ [Red LED +]             │
          │  Row 6: [Red LED -] ────→ Ground Rail        │
          │                                               │
          │  Row 11: Wire from GPIO24 ←──────────────────┘
          │  Row 9:  [Resistor] ─ [Green LED +]
          │  Row 10: [Green LED -] ──→ Ground Rail
          └───────────────────────────────────────────────┘
```

**Both methods work perfectly!** Use whichever is easier for you.

## Button Placement

### Small Button (Doesn't Span Gap) - MOST COMMON

**Just place it on ONE SIDE of the breadboard!**

```
Breadboard (left side):
    a b c d e │ f g h i j
             │
Row 1: [●][●]│            ← Top pins
       Button│
Row 3: [●][●]│            ← Bottom pins
       ↑   ↑
       │   └─ Connect to Ground Rail
       │
       └───── Connect to GPIO 17
```

**Which pins to use:** Use **diagonal** pins (opposite corners):
- Top-left pin → GPIO 17
- Bottom-right pin → Ground

```
Button pins (top view):
  ┌────────┐
  │1     2 │
  │  [ ]   │  ← Press here
  │3     4 │
  └────────┘

Use: Pin 1 (top-left) and Pin 4 (bottom-right)
OR:  Pin 2 (top-right) and Pin 3 (bottom-left)
```

### Large Button (Spans Gap) - If you have this type

```
    a b c d e │ f g h i j
Row 1: [●]─────┼─────[●]    ← Pins 1 & 2
Row 2:         │
Row 3: [●]─────┼─────[●]    ← Pins 3 & 4
       ↑  MIDDLE GAP  ↑
```

Use any pin from left side → GPIO 17  
Use any pin from right side → Ground

**Both methods work fine!**

## Step-by-Step Checklist

### 🎯 EASIEST METHOD - Use 3 Different Ground Pins

### 1️⃣ Ground Setup (NO ground rail needed!)
```
Skip the ground rail! Use 3 different ground pins:
  - Pin 14 (GND) for button
  - Pin 20 (GND) for red LED  
  - Pin 25 (GND) for green LED
```

### 2️⃣ Button (SMALL - doesn't span gap)
```
Place: On LEFT side of breadboard (rows 1 & 3)

Connect: Use DIAGONAL pins
  - Top-left pin (row 1) ←────── Pi Pin 11 (GPIO 17)
  - Bottom-right pin (row 3) ──→ Pi Pin 14 (GND)
```

### 3️⃣ Red LED + Resistor
```
Place:
  - LED long leg in row 5
  - LED short leg in row 6
  - Resistor: row 5 to row 7

Connect:
  - Row 7 ←───────────── Pi Pin 16 (GPIO 23)
  - Row 6 (LED -) ────→ Pi Pin 20 (GND)
```

### 4️⃣ Green LED + Resistor
```
Place:
  - LED long leg in row 9
  - LED short leg in row 10
  - Resistor: row 9 to row 11

Connect:
  - Row 11 ←──────────── Pi Pin 18 (GPIO 24)
  - Row 10 (LED -) ───→ Pi Pin 25 (GND)
```

### 5️⃣ USB Microphone
```
Plug into any USB port ✅
```

---

### Alternative: Use Ground Rail (If you prefer)

<details>
<summary>Click to expand ground rail method</summary>

### 1️⃣ Ground Rail Setup
```
Pi Pin 14 (GND) ─────→ Breadboard Ground Rail (-)
```

### 2️⃣ Button
```
Place: On left side (rows 1 & 3)
Connect: 
  - Top pin ←─── Pi Pin 11 (GPIO 17)
  - Bottom pin → Ground Rail (-)
```

### 3️⃣ Red LED
```
Connect:
  - Row 7 ←─── Pi Pin 16 (GPIO 23)
  - LED (-) ──→ Ground Rail (-)
```

### 4️⃣ Green LED
```
Connect:
  - Row 11 ←── Pi Pin 18 (GPIO 24)
  - LED (-) ──→ Ground Rail (-)
```

</details>

## LED Leg Identification

```
LED (looking at it):
        ┌─────┐
 Long ──┤     │  ← Long leg = POSITIVE (+)
        │ [ ] │     Connect to GPIO (via resistor)
        │     │
Short ──┤     │  ← Short leg = NEGATIVE (-)
        └─────┘     Connect to Ground Rail
```

**Tip:** The LED has a flat side on the negative side.

## Final Wire Count

**Wires from Raspberry Pi to Breadboard:** 4
1. Pin 11 → Button
2. Pin 14 → Ground Rail ⭐
3. Pin 16 → Red LED
4. Pin 18 → Green LED

**Short wires on breadboard:** 3
1. Button → Ground Rail
2. Red LED → Ground Rail
3. Green LED → Ground Rail

**Total wires needed:** 7

## Common Mistakes to Avoid

❌ **DON'T:** Connect Pin 14 to each component separately
✅ **DO:** Connect Pin 14 to ground rail once, components share it

❌ **DON'T:** Worry if button doesn't span the middle gap
✅ **DO:** Place it on one side, use diagonal pins

❌ **DON'T:** Use pins on the same row of the button (they're already connected)
✅ **DO:** Use diagonal pins (opposite corners) - one from top row, one from bottom row

❌ **DON'T:** Connect LED backwards (long leg to ground)
✅ **DO:** Long leg (+) to GPIO, short leg (-) to ground

❌ **DON'T:** Forget the resistors (LEDs will burn out!)
✅ **DO:** Always use 220Ω resistors with LEDs

## Quick Test After Wiring

Run this on Raspberry Pi:
```bash
python3 << 'EOF'
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.OUT)
GPIO.setup(24, GPIO.OUT)

print("Testing Red LED...")
GPIO.output(23, GPIO.HIGH)
time.sleep(2)
GPIO.output(23, GPIO.LOW)

print("Testing Green LED...")
GPIO.output(24, GPIO.HIGH)
time.sleep(2)
GPIO.output(24, GPIO.LOW)

print("Test complete!")
GPIO.cleanup()
EOF
```

If both LEDs blink → You're good! ✅  
If not → Check your wiring against this guide.
