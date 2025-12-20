# Quick Start Guide - Deepfake Audio Detection API

## ⚡ Using AASIST-L (Lightweight Version)

This API is configured to use **AASIST-L** (AASIST-Light), which is optimized for smaller GPUs like your RTX 3050 Laptop GPU.

**Benefits:**
- ✓ Lower memory usage (works great on 4-6GB VRAM)
- ✓ Faster inference
- ✓ Still provides excellent detection accuracy

**Note:** If you have a larger GPU (8GB+ VRAM) and want maximum accuracy, you can switch to the full AASIST model by editing `api.py` line 50.

## Step-by-Step Setup (Windows PowerShell)

### 1. Create and Activate UV Environment

```powershell
# Navigate to project
cd C:\Users\loq\OneDrive\Desktop\deepfake\aasist

# Create uv environment
uv venv

# Activate (PowerShell)
.\.venv\Scripts\Activate.ps1

# If you get execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. Install Dependencies

```powershell
# Install PyTorch with CUDA 12.8
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128

# Install API and audio processing dependencies
uv pip install fastapi "uvicorn[standard]" python-multipart requests numpy soundfile librosa scipy tensorboard
```

### 3. Verify CUDA is Working

```powershell
python -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"
```

Expected output:
```
CUDA available: True
Device: NVIDIA GeForce RTX 3050 Laptop GPU
```

### 4. Start the API Server

```powershell
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
Using device: cuda
Loading AASIST-L (light version) model...
✓ AASIST-L model loaded from models/weights/AASIST-L.pth
  This is the lightweight version optimized for smaller GPUs
✓ AASIST-L model loaded successfully (lightweight version)
INFO:     Application startup complete.
```

### 5. Test the API

Open a **new terminal** (keep the server running) and activate the venv:

```powershell
cd C:\Users\loq\OneDrive\Desktop\deepfake\aasist
.\.venv\Scripts\Activate.ps1

# Test health endpoint
python test_api.py health

# Test with an audio file
python test_api.py path\to\your\audio.wav
```

### 6. Access Interactive Documentation

Open in your browser:
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

## Quick Commands Reference

```powershell
# Activate environment
.\.venv\Scripts\Activate.ps1

# Start API server
uvicorn api:app --reload

# Start server in background (production)
Start-Process powershell -ArgumentList "-Command", "uvicorn api:app --host 0.0.0.0 --port 8000"

# Test health
Invoke-RestMethod -Uri http://localhost:8000/health

# Test prediction (PowerShell)
$file = Get-Item "audio.wav"
$boundary = [System.Guid]::NewGuid().ToString()
Invoke-RestMethod -Uri http://localhost:8000/predict -Method Post -InFile $file.FullName

# Stop server
# Press CTRL+C in the terminal where uvicorn is running
```

## Using the API from Code

### Python Example

```python
import requests

# Single prediction
with open("audio.wav", "rb") as f:
    response = requests.post(
        "http://localhost:8000/predict",
        files={"file": ("audio.wav", f, "audio/wav")}
    )
    result = response.json()
    
print(f"Prediction: {result['prediction']}")
print(f"Confidence: {result['confidence']:.2%}")
```

### JavaScript Example

```javascript
const formData = new FormData();
formData.append('file', audioFile);

fetch('http://localhost:8000/predict', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => {
  console.log('Prediction:', data.prediction);
  console.log('Confidence:', data.confidence);
});
```

### cURL Example

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@audio.wav"
```

## Troubleshooting

### Issue: "Model not loaded" error

**Solution**: Make sure model weights exist at `models/weights/AASIST-L.pth`

If you don't have weights:
1. Download pre-trained AASIST-L weights
2. Or train the model: `python main.py --config config/AASIST-L.conf`
3. Or switch to full AASIST if you have those weights (edit `api.py` line 50)

### Issue: CUDA not detected

**Solution**: 
```powershell
# Check NVIDIA driver
nvidia-smi

# Reinstall PyTorch with CUDA
uv pip uninstall torch torchvision torchaudio
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
```

### Issue: Import errors

**Solution**: Reinstall all dependencies
```powershell
uv pip install -r requirements-api.txt
```

### Issue: Port 8000 already in use

**Solution**: Use a different port
```powershell
uvicorn api:app --reload --port 8001
```

## File Structure

```
aasist/
├── api.py                  # FastAPI server (uses AASIST-L)
├── test_api.py            # Test client
├── requirements-api.txt   # API dependencies
├── README_API.md          # API documentation
├── setup_api.bat          # Windows setup script
├── QUICKSTART.md          # This file
├── main.py                # Training script (updated)
├── config/
│   ├── AASIST-L.conf      # AASIST-L config (used by API)
│   └── AASIST.conf        # Full AASIST config
└── models/
    └── weights/
        ├── AASIST-L.pth   # AASIST-L weights (needed for API)
        └── AASIST.pth     # Full AASIST weights
```

## Next Steps

1. ✓ Setup complete
2. Test with sample audio files
3. Integrate into your application
4. Deploy to production server

For detailed API documentation, see `README_API.md`
