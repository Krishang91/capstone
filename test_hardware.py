#!/usr/bin/env python3
"""
Hardware Debug Script for Raspberry Pi
Tests button, LEDs, and microphone separately
"""
import RPi.GPIO as GPIO
import time
import sys

# Configuration
BUTTON_PIN = 17
RED_LED_PIN = 23
GREEN_LED_PIN = 24

print("="*60)
print("🔧 Hardware Debug Script")
print("="*60)

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Test 1: LED Test
print("\n[TEST 1] Testing LEDs...")
GPIO.setup(RED_LED_PIN, GPIO.OUT)
GPIO.setup(GREEN_LED_PIN, GPIO.OUT)

print("  → Red LED ON")
GPIO.output(RED_LED_PIN, GPIO.HIGH)
time.sleep(2)
GPIO.output(RED_LED_PIN, GPIO.LOW)

print("  → Green LED ON")
GPIO.output(GREEN_LED_PIN, GPIO.HIGH)
time.sleep(2)
GPIO.output(GREEN_LED_PIN, GPIO.LOW)

print("  ✅ LEDs working!")

# Test 2: Button Test
print("\n[TEST 2] Testing Button...")
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

print("  → Press the button within 10 seconds...")
button_pressed = False
start_time = time.time()

while time.time() - start_time < 10:
    if GPIO.input(BUTTON_PIN) == GPIO.LOW:
        print("  ✅ Button press detected!")
        # Blink green LED
        for _ in range(3):
            GPIO.output(GREEN_LED_PIN, GPIO.HIGH)
            time.sleep(0.1)
            GPIO.output(GREEN_LED_PIN, GPIO.LOW)
            time.sleep(0.1)
        button_pressed = True
        break
    time.sleep(0.01)

if not button_pressed:
    print("  ❌ No button press detected")
    print("  → Check your wiring:")
    print("     - Button top-left pin → Pi Pin 11 (GPIO 17)")
    print("     - Button bottom-right pin → Pi Pin 14 (GND)")

# Test 3: Microphone Test
print("\n[TEST 3] Testing Microphone...")
try:
    import pyaudio
    audio = pyaudio.PyAudio()
    
    # List audio devices
    print("  Available audio devices:")
    for i in range(audio.get_device_count()):
        info = audio.get_device_info_by_index(i)
        if info['maxInputChannels'] > 0:
            print(f"    [{i}] {info['name']}")
    
    # Try to open a stream
    try:
        stream = audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=1024
        )
        stream.close()
        print("  ✅ Microphone working!")
    except Exception as e:
        print(f"  ❌ Microphone error: {e}")
    
    audio.terminate()
    
except ImportError:
    print("  ⚠️  PyAudio not installed")
    print("  → Install with: pip3 install pyaudio")

# Test 4: API Connection
print("\n[TEST 4] Testing API Connection...")
try:
    import requests
    API_URL = "https://10.252.164.77:8000/health"
    response = requests.get(API_URL, timeout=5, verify=False)
    if response.status_code == 200:
        print(f"  ✅ API reachable: {response.json()}")
    else:
        print(f"  ❌ API error: {response.status_code}")
except Exception as e:
    print(f"  ❌ Cannot reach API: {e}")
    print("  → Make sure API is running on your server")

# Cleanup
GPIO.cleanup()

print("\n" + "="*60)
print("✅ Debug complete!")
print("="*60)
print("\nIf all tests passed, try running: python3 raspberry_pi_client.py")
