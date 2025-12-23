#!/usr/bin/env python3
"""Test all button pin combinations"""
import RPi.GPIO as GPIO
import time

BUTTON_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

print("="*60)
print("🔘 Button Test - Press button NOW and HOLD it")
print("="*60)

for i in range(50):
    state = GPIO.input(BUTTON_PIN)
    print(f"Button state: {'PRESSED (LOW)' if state == GPIO.LOW else 'NOT PRESSED (HIGH)'}", end='\r')
    time.sleep(0.1)

print("\n\n✅ If you saw 'PRESSED' when holding button, it works!")
print("❌ If always 'NOT PRESSED', try different button pins")

GPIO.cleanup()
