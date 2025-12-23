"""
Raspberry Pi Client for Deepfake Audio Detection
Hardware Setup:
- Button: GPIO 17 (with pull-up resistor)
- Red LED: GPIO 23 (for fake audio)
- Green LED: GPIO 24 (for real audio)
- Ground: Connect button and LEDs to ground
"""
import os
import sys
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
# Suppress ALSA warnings
os.environ['ALSA_CARD'] = 'default'

# Redirect stderr to suppress ALSA warnings
import contextlib

@contextlib.contextmanager
def suppress_stderr():
    """Suppress stderr output at file descriptor level"""
    # Save the actual stderr file descriptor
    stderr_fd = sys.stderr.fileno()
    old_stderr_fd = os.dup(stderr_fd)
    
    # Open devnull
    devnull_fd = os.open(os.devnull, os.O_WRONLY)
    
    # Replace stderr with devnull at the file descriptor level
    os.dup2(devnull_fd, stderr_fd)
    os.close(devnull_fd)
    
    try:
        yield
    finally:
        # Restore stderr
        os.dup2(old_stderr_fd, stderr_fd)
        os.close(old_stderr_fd)

import RPi.GPIO as GPIO
import wave
import requests
import time
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Import pyaudio with suppressed stderr
with suppress_stderr():
    import pyaudio

# Configuration
API_URL = "https://10.252.164.77:8000/predict"  # Change to your API server IP (https!!)
VERIFY_SSL = False  # Set to True if using proper certificate
BUTTON_PIN = 17
RED_LED_PIN = 23  # Fake
GREEN_LED_PIN = 24  # Real

# Audio Configuration
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK = 1024
AUDIO_FORMAT = pyaudio.paInt16
OUTPUT_FILE = "/tmp/recording.wav"

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(RED_LED_PIN, GPIO.OUT)
GPIO.setup(GREEN_LED_PIN, GPIO.OUT)

# Turn off both LEDs initially
GPIO.output(RED_LED_PIN, GPIO.LOW)
GPIO.output(GREEN_LED_PIN, GPIO.LOW)

# Initialize PyAudio with suppressed errors
with suppress_stderr():
    audio = pyaudio.PyAudio()


def record_audio():
    """Record audio while button is pressed"""
    print("🎙️ Recording... (Release button to stop)")
    
    frames = []
    try:
        stream = audio.open(
            format=AUDIO_FORMAT,
            channels=CHANNELS,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=CHUNK,
            input_device_index=None  # Use default device
        )
    except Exception as e:
        print(f"❌ Failed to open audio stream: {e}")
        return None
    
    # Record while button is pressed
    try:
        while GPIO.input(BUTTON_PIN) == GPIO.LOW:
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
                frames.append(data)
            except Exception as e:
                print(f"⚠️ Audio read error: {e}")
                break
    finally:
        print("⏹️ Recording stopped")
        # Stop and close the stream
        try:
            stream.stop_stream()
            stream.close()
        except Exception:
            pass
    
    # Check if recording is too short
    if len(frames) < 10:  # At least ~0.6 seconds
        print("⚠️ Recording too short, please try again")
        return None
    
    # Save the recorded audio as WAV file
    with wave.open(OUTPUT_FILE, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(AUDIO_FORMAT))
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(b''.join(frames))
    
    return OUTPUT_FILE


def send_to_api(audio_file):
    """Send audio file to API and get prediction"""
    print("📤 Sending to API...")
    
    try:
        with open(audio_file, 'rb') as f:
            files = {'file': ('recording.wav', f, 'audio/wav')}
            response = requests.post(API_URL, files=files, timeout=10, verify=VERIFY_SSL)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Response received: {result}")
            return result
        else:
            print(f"❌ Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return None


def control_leds(prediction):
    """Control LEDs based on prediction"""
    # Turn off both LEDs first
    GPIO.output(RED_LED_PIN, GPIO.LOW)
    GPIO.output(GREEN_LED_PIN, GPIO.LOW)
    
    if prediction == "fake":
        print("🔴 FAKE DETECTED - Red LED ON")
        GPIO.output(RED_LED_PIN, GPIO.HIGH)
        # Blink for emphasis
        for _ in range(3):
            time.sleep(0.2)
            GPIO.output(RED_LED_PIN, GPIO.LOW)
            time.sleep(0.2)
            GPIO.output(RED_LED_PIN, GPIO.HIGH)
    elif prediction == "real":
        print("🟢 REAL AUDIO - Green LED ON")
        GPIO.output(GREEN_LED_PIN, GPIO.HIGH)
        # Blink for emphasis
        for _ in range(3):
            time.sleep(0.2)
            GPIO.output(GREEN_LED_PIN, GPIO.LOW)
            time.sleep(0.2)
            GPIO.output(GREEN_LED_PIN, GPIO.HIGH)
    
    # Keep LED on for 3 seconds
    time.sleep(3)
    
    # Turn off LEDs
    GPIO.output(RED_LED_PIN, GPIO.LOW)
    GPIO.output(GREEN_LED_PIN, GPIO.LOW)


def main():
    """Main loop"""
    print("\n" + "="*50)
    print("🎤 Deepfake Audio Detection - Raspberry Pi Client")
    print("="*50)
    print(f"API: {API_URL}")
    print(f"Button: GPIO {BUTTON_PIN}")
    print(f"Red LED (Fake): GPIO {RED_LED_PIN}")
    print(f"Green LED (Real): GPIO {GREEN_LED_PIN}")
    print("\n📌 Press and HOLD button to record audio")
    print("📌 Release button to stop and analyze")
    print("📌 Press Ctrl+C to exit\n")
    
    try:
        # Track button state for edge detection
        last_button_state = GPIO.HIGH
        
        while True:
            # Poll button state instead of using wait_for_edge (more reliable)
            current_button_state = GPIO.input(BUTTON_PIN)
            
            # Detect falling edge (button press)
            if last_button_state == GPIO.HIGH and current_button_state == GPIO.LOW:
                # Debounce - small delay to avoid false triggers
                time.sleep(0.05)
                
                # Verify button is still pressed after debounce
                if GPIO.input(BUTTON_PIN) == GPIO.LOW:
                    # Button pressed - start recording
                    audio_file = record_audio()
                    
                    # Check if recording was successful
                    if not audio_file:
                        time.sleep(0.5)
                        last_button_state = GPIO.input(BUTTON_PIN)
                        continue
                    
                    # Send to API
                    result = send_to_api(audio_file)
                    
                    if result:
                        # API might return 'prediction' or 'label'
                        prediction = result.get('prediction') or result.get('label')
                        confidence = result.get('confidence', 0)
                        
                        # Handle confidence as percentage or decimal
                        if confidence <= 1.0:
                            confidence = confidence * 100
                        
                        if prediction:
                            print(f"\n{'='*50}")
                            print(f"Prediction: {prediction.upper()}")
                            print(f"Confidence: {confidence:.1f}%")
                            print(f"{'='*50}\n")
                            
                            # Control LEDs
                            control_leds(prediction)
                        else:
                            print("⚠️ Invalid response from API")
                            result = None
                    else:
                        # Error - blink both LEDs
                        print("⚠️ Error - blinking both LEDs")
                        for _ in range(5):
                            GPIO.output(RED_LED_PIN, GPIO.HIGH)
                            GPIO.output(GREEN_LED_PIN, GPIO.HIGH)
                            time.sleep(0.1)
                            GPIO.output(RED_LED_PIN, GPIO.LOW)
                            GPIO.output(GREEN_LED_PIN, GPIO.LOW)
                            time.sleep(0.1)
                    
                    # Small delay before next recording
                    time.sleep(0.5)
                    print("Ready for next recording...\n")
            
            # Update button state for next iteration
            last_button_state = current_button_state
            
            # Small delay to avoid excessive CPU usage
            time.sleep(0.01)
    
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")
    finally:
        # Cleanup
        GPIO.output(RED_LED_PIN, GPIO.LOW)
        GPIO.output(GREEN_LED_PIN, GPIO.LOW)
        GPIO.cleanup()
        audio.terminate()
        print("✅ Cleanup complete")


if __name__ == "__main__":
    main()
