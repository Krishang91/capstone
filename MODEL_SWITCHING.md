# Switching Between AASIST and AASIST-L

## Current Configuration: AASIST-L (Lightweight)

The API is currently configured to use **AASIST-L**, which is optimized for smaller GPUs like the RTX 3050 Laptop GPU.

## How to Switch to Full AASIST

If you have a larger GPU (8GB+ VRAM) and want maximum accuracy, follow these steps:

### 1. Edit `api.py`

Open `api.py` and find line 50 (in the `load_model` function):

**Current (AASIST-L):**
```python
def load_model(config_path: str = "config/AASIST-L.conf", 
               model_path: str = "models/weights/AASIST-L.pth"):
    """Load the trained AASIST-L model (lighter version for smaller GPUs)"""
```

**Change to (Full AASIST):**
```python
def load_model(config_path: str = "config/AASIST.conf", 
               model_path: str = "models/weights/AASIST.pth"):
    """Load the trained AASIST model"""
```

### 2. Ensure You Have the Full Model Weights

Make sure these files exist:
- `config/AASIST.conf`
- `models/weights/AASIST.pth`

If you don't have them, you'll need to:
- Download pre-trained AASIST weights, or
- Train the model: `python main.py --config config/AASIST.conf`

### 3. Restart the API Server

```powershell
# Stop the current server (Ctrl+C)
# Then restart
uvicorn api:app --reload
```

## Comparison

| Feature | AASIST-L (Current) | AASIST (Full) |
|---------|-------------------|---------------|
| GPU Memory | ~2-3GB | ~4-6GB |
| Speed | Faster | Slower |
| Accuracy | Excellent | Best |
| Best For | RTX 3050, GTX 1660 | RTX 3080, A100 |

## Model Performance Tips

### For Small GPUs (4-6GB VRAM):
- ✓ Use AASIST-L (current configuration)
- ✓ Process files one at a time
- ✓ Close other GPU applications

### For Large GPUs (8GB+ VRAM):
- ✓ Use full AASIST for best accuracy
- ✓ Can use batch prediction endpoint
- ✓ Higher confidence scores

## Quick Reference

### Current Model Info
To check which model is loaded:
```powershell
curl http://localhost:8000/
```

Response will show:
```json
{
  "message": "Deepfake Audio Detection API (AASIST-L)",
  "model": "AASIST-L (lightweight version for smaller GPUs)",
  ...
}
```

### GPU Memory Usage
Check VRAM usage while API is running:
```powershell
nvidia-smi
```

Look for the `python` process memory usage in the table.

## Troubleshooting

### CUDA Out of Memory with AASIST-L
If you get OOM errors even with AASIST-L:
1. Close other GPU applications (browsers, games, etc.)
2. Restart the API server
3. Check `nvidia-smi` to see what else is using GPU

### CUDA Out of Memory with Full AASIST
If you switched to full AASIST and get OOM:
1. Your GPU may not have enough memory
2. Switch back to AASIST-L (recommended)
3. Or use CPU mode: set `CUDA_VISIBLE_DEVICES=""`

### Performance Issues
If inference is slow:
- AASIST-L should be faster
- Check if GPU is actually being used (check API startup logs)
- Verify CUDA is working: `python -c "import torch; print(torch.cuda.is_available())"`
