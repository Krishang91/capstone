# Deepfake Audio Detection API

FastAPI server for detecting deepfake/spoofed audio using the AASIST-L model (lightweight version optimized for smaller GPUs like RTX 3050).

## Model Info

This API uses **AASIST-L** (AASIST-Light), which is:
- Optimized for smaller GPUs (works well with RTX 3050 and similar)
- Lighter and faster than the full AASIST model
- Still provides excellent deepfake detection accuracy

If you have a larger GPU and want better accuracy, you can modify `api.py` to use `config/AASIST.conf` and `models/weights/AASIST.pth` instead.

## Setup

### 1. Create UV Environment and Install Dependencies

```powershell
# Navigate to project directory
cd C:\Users\loq\OneDrive\Desktop\deepfake\aasist

# Create uv environment
uv venv

# Activate environment
.venv\Scripts\Activate.ps1  # PowerShell
# or
.venv\Scripts\activate.bat  # CMD

# Install PyTorch with CUDA 12.8
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128

# Install other dependencies
uv pip install fastapi uvicorn[standard] python-multipart numpy soundfile librosa scipy tensorboard
```

### 2. Verify CUDA is Working

```powershell
python -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"
```

### 3. Ensure Model Weights Exist

Make sure you have the trained model weights at:
- `models/weights/AASIST-L.pth` (lightweight version)
- `config/AASIST-L.conf` (configuration file)

If you want to use the full AASIST model instead, edit `api.py` line 50 to use:
- `config/AASIST.conf` 
- `models/weights/AASIST.pth`

## Running the API

### Start the Server

```powershell
# Make sure you're in the venv
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## API Endpoints

### 1. Health Check

```powershell
curl http://localhost:8000/health
```

### 2. Predict Single Audio File

**Using curl (PowerShell):**
```powershell
curl -X POST "http://localhost:8000/predict" -F "file=@path\to\audio.wav"
```

**Using Python test script:**
```powershell
python test_api.py audio.wav
```

**Using Python requests:**
```python
import requests

with open("audio.wav", "rb") as f:
    files = {"file": ("audio.wav", f, "audio/wav")}
    response = requests.post("http://localhost:8000/predict", files=files)
    print(response.json())
```

### 3. Batch Prediction

```powershell
curl -X POST "http://localhost:8000/predict_batch" ^
  -F "files=@audio1.wav" ^
  -F "files=@audio2.wav" ^
  -F "files=@audio3.wav"
```

## Response Format

```json
{
  "filename": "audio.wav",
  "prediction": "fake",
  "confidence": 0.95,
  "score": -2.944
}
```

- **prediction**: "fake" or "real"
- **confidence**: 0-1 (higher = more confident)
- **score**: raw model output (negative = fake, positive = real)

## Testing

### Test Health Endpoint
```powershell
python test_api.py health
```

### Test Prediction
```powershell
python test_api.py path\to\audio.wav
```

## Troubleshooting

### Model Not Found
Make sure model weights exist at `models/weights/AASIST-L.pth`. You may need to:
1. Train the model first using `main.py --config config/AASIST-L.conf`
2. Download pre-trained weights
3. Check that the file path is correct

### Using Full AASIST Instead of AASIST-L
If you have a larger GPU and want the full model, edit `api.py` around line 50:
```python
def load_model(config_path: str = "config/AASIST.conf",  # Change this
               model_path: str = "models/weights/AASIST.pth"):  # And this
```

### CUDA Out of Memory
If you get CUDA OOM errors:
- Reduce batch size in config
- Use CPU by setting `CUDA_VISIBLE_DEVICES=""`

### Import Errors
Make sure all dependencies are installed:
```powershell
uv pip install -r requirements-api.txt
```

## Example Usage

```python
import requests

# Single prediction
with open("suspicious_audio.wav", "rb") as f:
    response = requests.post(
        "http://localhost:8000/predict",
        files={"file": f}
    )
    result = response.json()
    
    if result["prediction"] == "fake":
        print(f"⚠️ Deepfake detected! Confidence: {result['confidence']:.1%}")
    else:
        print(f"✓ Audio appears genuine. Confidence: {result['confidence']:.1%}")
```

## Production Deployment

For production use:

```powershell
# Use multiple workers
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4

# Or use gunicorn
gunicorn api:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Notes

- Only WAV format is currently supported
- Audio is automatically padded/truncated to 64600 samples
- Stereo audio is converted to mono
- Model uses GPU if available, falls back to CPU
