"""
FastAPI server for deepfake audio detection
Accepts WAV audio files and returns fake/real prediction

Usage:
    uvicorn api:app --reload --host 0.0.0.0 --port 8000
"""
import json
import os
from pathlib import Path
from typing import Dict

import numpy as np
import soundfile as sf
import torch
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from models.AASIST import Model as AASISTModel
from data_utils import pad


app = FastAPI(
    title="Deepfake Audio Detection API (AASIST-L)",
    description="Detects whether audio is fake (deepfake/spoofed) or real (bonafide) using AASIST-L lightweight model",
    version="1.0.0"
)


class PredictionResponse(BaseModel):
    """Response model for prediction"""
    filename: str
    prediction: str  # "fake" or "real"
    confidence: float  # 0-1, higher means more confident
    score: float  # raw model score


# Global model variable
model = None
device = None
config = None


def load_model(config_path: str = "config/AASIST-L.conf", 
               model_path: str = "models/weights/AASIST-L.pth"):
    """Load the trained AASIST-L model (lighter version for smaller GPUs)"""
    global model, device, config
    
    # Set device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    print(f"Loading AASIST-L (light version) model...")
    
    # Load config
    with open(config_path, "r") as f:
        config = json.load(f)
    
    # Initialize model
    model_config = config["model_config"]
    model = AASISTModel(model_config).to(device)
    
    # Load weights
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    
    print(f"✓ AASIST-L model loaded from {model_path}")
    print(f"  This is the lightweight version optimized for smaller GPUs")
    return model


def preprocess_audio(audio_path: str, max_len: int = 64600) -> torch.Tensor:
    """
    Preprocess audio file for model input
    
    Args:
        audio_path: Path to audio file
        max_len: Maximum length for padding
    
    Returns:
        Preprocessed audio tensor
    """
    # Load audio
    audio, sr = sf.read(audio_path)
    
    # Convert to mono if stereo
    if len(audio.shape) > 1:
        audio = np.mean(audio, axis=1)
    
    # Pad or truncate
    audio = pad(audio, max_len=max_len)
    
    # Convert to tensor
    audio_tensor = torch.FloatTensor(audio).unsqueeze(0)  # Add batch dimension
    
    return audio_tensor


@app.on_event("startup")
async def startup_event():
    """Load model on startup"""
    try:
        load_model()
        print("✓ AASIST-L model loaded successfully (lightweight version)")
    except Exception as e:
        print(f"✗ Error loading model: {e}")
        print("Please ensure model weights exist at models/weights/AASIST-L.pth")


@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "message": "Deepfake Audio Detection API (AASIST-L)",
        "model": "AASIST-L (lightweight version for smaller GPUs)",
        "endpoints": {
            "/predict": "POST - Upload WAV file for prediction",
            "/health": "GET - Check API health status",
            "/docs": "GET - Interactive API documentation"
        },
        "model_loaded": model is not None,
        "device": str(device) if device else "not initialized"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy" if model is not None else "model not loaded",
        "model_loaded": model is not None,
        "device": str(device) if device else "not initialized"
    }


@app.post("/predict", response_model=PredictionResponse)
async def predict(file: UploadFile = File(...)):
    """
    Predict whether audio is fake or real
    
    Args:
        file: WAV audio file
    
    Returns:
        Prediction result with confidence score
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    # Check file extension
    if not file.filename.endswith(('.wav', '.WAV')):
        raise HTTPException(
            status_code=400, 
            detail="Only WAV files are supported"
        )
    
    try:
        # Save uploaded file temporarily
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Preprocess audio
        audio_tensor = preprocess_audio(temp_path)
        audio_tensor = audio_tensor.to(device)
        
        # Run inference
        with torch.no_grad():
            output = model(audio_tensor)
            score = output.item()
        
        # Interpret result
        # Lower score = fake, Higher score = real
        # Threshold typically around 0 (sigmoid output)
        prediction = "real" if score > 0 else "fake"
        
        # Calculate confidence (0-1)
        # Use sigmoid to convert score to probability
        confidence = torch.sigmoid(torch.tensor(score)).item()
        if prediction == "fake":
            confidence = 1 - confidence
        
        # Clean up temp file
        os.remove(temp_path)
        
        return PredictionResponse(
            filename=file.filename,
            prediction=prediction,
            confidence=float(confidence),
            score=float(score)
        )
    
    except Exception as e:
        # Clean up temp file if it exists
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@app.post("/predict_batch")
async def predict_batch(files: list[UploadFile] = File(...)):
    """
    Predict multiple audio files at once
    
    Args:
        files: List of WAV audio files
    
    Returns:
        List of prediction results
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    results = []
    for file in files:
        try:
            result = await predict(file)
            results.append(result.dict())
        except Exception as e:
            results.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return {"predictions": results, "total": len(files)}


if __name__ == "__main__":
    import uvicorn
    
    # Load model
    load_model()
    
    # Run server
    print("\nStarting Deepfake Audio Detection API...")
    print("Open http://localhost:8000/docs for interactive documentation")
    uvicorn.run(app, host="0.0.0.0", port=8000)
