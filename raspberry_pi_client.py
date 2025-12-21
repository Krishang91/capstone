"""
Raspberry Pi Client for Deepfake Audio Detection
Hardware Setup:
- Button: GPIO 17 (with pull-up resistor)
- Red LED: GPIO 23 (for fake audio)
- Green LED: GPIO 24 (for real audio)
- Ground: Connect button and LEDs to ground
"""
import RPi.GPIO as GPIO
import pyaudio
import wave
import requests
import time
from pathlib import Path

# Configuration
API_URL = "http://192.168.1.100:8000/predict"  # Change to your API server IP
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

# Initialize PyAudio
audio = pyaudio.PyAudio()


def record_audio():
    """Record audio while button is pressed"""
    print("🎙️ Recording... (Release button to stop)")
    
    frames = []
    stream = audio.open(
        format=AUDIO_FORMAT,
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=CHUNK
    )
    
    # Record while button is pressed
    while GPIO.input(BUTTON_PIN) == GPIO.LOW:
        data = stream.read(CHUNK)
        frames.append(data)
    
    print("⏹️ Recording stopped")
    
    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    
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
            response = requests.post(API_URL, files=files, timeout=10)
        
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
        while True:
            # Wait for button press
            GPIO.wait_for_edge(BUTTON_PIN, GPIO.FALLING)
            
            # Button pressed - start recording
            audio_file = record_audio()
            
            # Send to API
            result = send_to_api(audio_file)
            
            if result:
                prediction = result.get('prediction')
                confidence = result.get('confidence', 0) * 100
                
                print(f"\n{'='*50}")
                print(f"Prediction: {prediction.upper()}")
                print(f"Confidence: {confidence:.1f}%")
                print(f"{'='*50}\n")
                
                # Control LEDs
                control_leds(prediction)
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
