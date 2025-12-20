@echo off
REM Setup script for Deepfake Audio Detection API
REM Run this in CMD after activating your uv environment

echo ========================================
echo Deepfake Audio Detection API Setup
echo ========================================
echo.

echo [1/4] Installing PyTorch with CUDA 12.8...
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
if %errorlevel% neq 0 (
    echo ERROR: Failed to install PyTorch
    pause
    exit /b 1
)

echo.
echo [2/4] Installing API dependencies...
uv pip install fastapi uvicorn[standard] python-multipart requests
if %errorlevel% neq 0 (
    echo ERROR: Failed to install API dependencies
    pause
    exit /b 1
)

echo.
echo [3/4] Installing audio processing libraries...
uv pip install numpy soundfile librosa scipy tensorboard
if %errorlevel% neq 0 (
    echo ERROR: Failed to install audio libraries
    pause
    exit /b 1
)

echo.
echo [4/4] Verifying CUDA installation...
python -c "import torch; print('PyTorch version:', torch.__version__); print('CUDA available:', torch.cuda.is_available()); print('CUDA version:', torch.version.cuda if torch.cuda.is_available() else 'N/A'); print('Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU only')"

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To start the API server, run:
echo   uvicorn api:app --reload
echo.
echo To test the API, run:
echo   python test_api.py health
echo   python test_api.py your_audio.wav
echo.
echo Open http://localhost:8000/docs for interactive API documentation
echo.
pause
