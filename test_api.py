"""
Test script for the deepfake audio detection API

Usage:
    python test_api.py <audio_file.wav>
"""
import sys
import requests
from pathlib import Path


def test_predict(audio_file: str, api_url: str = "http://localhost:8000"):
    """
    Test the /predict endpoint
    
    Args:
        audio_file: Path to WAV file
        api_url: API base URL
    """
    endpoint = f"{api_url}/predict"
    
    # Check if file exists
    if not Path(audio_file).exists():
        print(f"Error: File not found: {audio_file}")
        return
    
    # Prepare file for upload
    with open(audio_file, "rb") as f:
        files = {"file": (Path(audio_file).name, f, "audio/wav")}
        
        print(f"Uploading {audio_file} to {endpoint}...")
        try:
            response = requests.post(endpoint, files=files)
            response.raise_for_status()
            
            result = response.json()
            
            print("\n" + "="*50)
            print("PREDICTION RESULT")
            print("="*50)
            print(f"Filename:    {result['filename']}")
            print(f"Prediction:  {result['prediction'].upper()}")
            print(f"Confidence:  {result['confidence']:.2%}")
            print(f"Raw Score:   {result['score']:.4f}")
            print("="*50)
            
            if result['prediction'] == 'fake':
                print("\n⚠️  WARNING: This audio appears to be FAKE/DEEPFAKE")
            else:
                print("\n✓ This audio appears to be REAL/BONAFIDE")
            
        except requests.exceptions.ConnectionError:
            print(f"\n✗ Error: Cannot connect to API at {api_url}")
            print("Make sure the API server is running:")
            print("  uvicorn api:app --reload")
        except requests.exceptions.HTTPError as e:
            print(f"\n✗ HTTP Error: {e}")
            print(f"Response: {response.text}")
        except Exception as e:
            print(f"\n✗ Error: {e}")


def test_health(api_url: str = "http://localhost:8000"):
    """
    Test the /health endpoint
    
    Args:
        api_url: API base URL
    """
    endpoint = f"{api_url}/health"
    
    try:
        response = requests.get(endpoint)
        response.raise_for_status()
        
        result = response.json()
        
        print("\n" + "="*50)
        print("API HEALTH CHECK")
        print("="*50)
        print(f"Status:        {result['status']}")
        print(f"Model Loaded:  {result['model_loaded']}")
        print(f"Device:        {result['device']}")
        print("="*50)
        
    except Exception as e:
        print(f"\n✗ Health check failed: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_api.py <audio_file.wav>")
        print("\nOptions:")
        print("  python test_api.py health          - Check API health")
        print("  python test_api.py <file.wav>      - Predict single file")
        sys.exit(1)
    
    if sys.argv[1] == "health":
        test_health()
    else:
        audio_file = sys.argv[1]
        test_predict(audio_file)
