# Environment Setup Guide

## For Developers Cloning This Repository

### Prerequisites
- Python 3.12.4
- NVIDIA GPU with CUDA support (or use CPU mode)
- [uv](https://github.com/astral-sh/uv) package manager (recommended) OR pip

### Quick Setup with UV (Recommended)

```bash
# 1. Install uv if you don't have it
pip install uv

# 2. Create virtual environment
uv venv

# 3. Activate environment
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Windows CMD:
.venv\Scripts\activate.bat
# Linux/Mac:
source .venv/bin/activate

# 4. Install PyTorch with CUDA
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128

# 5. Install other dependencies
uv pip install -r requirements-api.txt

# 6. Verify installation
python verify_code.py
```

### Alternative Setup with pip

```bash
# 1. Create virtual environment
python -m venv .venv

# 2. Activate environment (see above)

# 3. Install PyTorch with CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128

# 4. Install other dependencies
pip install -r requirements-api.txt

# 5. Verify installation
python verify_code.py
```

### Docker Setup (Easiest)

```bash
# Build and run with GPU support
docker-compose up -d

# Check logs
docker-compose logs -f

# Access API at http://localhost:8000
```

## File Structure

```
aasist/
├── .venv/                  # Virtual environment (NOT in Git)
├── .python-version         # Python version spec (IN Git)
├── requirements-api.txt    # Dependencies (IN Git)
├── api.py                  # API server (IN Git)
├── main.py                 # Training script (IN Git)
├── Dockerfile              # Docker config (IN Git)
├── docker-compose.yml      # Docker compose (IN Git)
├── models/
│   └── weights/            # Model files (NOT in Git, too large)
└── config/                 # Config files (IN Git)
```

## What's Tracked in Git

✅ **Included:**
- Source code (`.py` files)
- Configuration files (`*.conf`, `*.json`)
- Requirements (`requirements*.txt`)
- Documentation (`*.md`)
- Docker files (`Dockerfile`, `docker-compose.yml`)
- `.python-version` (Python version)
- `.gitignore`

❌ **Excluded:**
- `.venv/` (virtual environment)
- `__pycache__/` (Python cache)
- `models/weights/*.pth` (large model files)
- `.env` (environment secrets)
- Temporary files

## Sharing Model Weights

Model weights are too large for Git. Share them via:
1. **Git LFS** (Large File Storage)
2. **Cloud storage** (Google Drive, Dropbox, S3)
3. **Model registry** (Hugging Face, Weights & Biases)

## Common Issues

### Issue: DLL errors on Windows
**Solution:** Use Docker or install Visual C++ Redistributable

### Issue: CUDA not detected
**Solution:** 
- Check `nvidia-smi`
- Reinstall PyTorch with correct CUDA version
- Or use CPU mode by setting `CUDA_VISIBLE_DEVICES=""`

### Issue: Module not found
**Solution:** Make sure virtual environment is activated (you should see `(.venv)` in prompt)
