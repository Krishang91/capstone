"""
FastAPI server for deepfake audio detection
Supports both HTTP file upload and WebSocket real-time streaming

Usage:
    uvicorn api:app --reload --host 0.0.0.0 --port 8000
"""
import json
import os
from pathlib import Path
from typing import Dict
import asyncio
import base64
import io

import numpy as np
import soundfile as sf
import torch
import whisper
from fastapi import FastAPI, File, UploadFile, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from models.AASIST import Model as AASISTModel
from data_utils import pad


app = FastAPI(
    title="Deepfake Audio Detection API (AASIST-L)",
    description="Detects whether audio is fake (deepfake/spoofed) or real (bonafide) using AASIST-L lightweight model. Supports HTTP and WebSocket.",
    version="2.0.0"
)

# Add CORS for web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PredictionResponse(BaseModel):
    """Response model for prediction"""
    filename: str
    prediction: str  # "fake" or "real"
    confidence: float  # 0-1, higher means more confident
    score: float  # raw model score
    transcript: str = ""  # Speech-to-text transcript


# Global model variables
model = None
device = None
config = None
whisper_model = None


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
    """Load models on startup"""
    global whisper_model
    try:
        load_model()
        print("✓ AASIST-L model loaded successfully (lightweight version)")
        
        # Load Whisper model for transcription
        print("Loading Whisper model for speech-to-text...")
        whisper_model = whisper.load_model("base")  # Options: tiny, base, small, medium, large
        print("✓ Whisper model loaded successfully")
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
            "/ws": "WebSocket - Real-time audio streaming",
            "/web": "GET - Web interface",
            "/health": "GET - Check API health status",
            "/docs": "GET - Interactive API documentation"
        },
        "model_loaded": model is not None,
        "device": str(device) if device else "not initialized",
        "streaming_config": {
            "sample_rate": 16000,
            "chunk_duration_seconds": 2,
            "chunk_size_samples": 32000
        }
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
    
    temp_path = None
    try:
        # Save uploaded file temporarily
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        print(f"[DEBUG] Processing file: {temp_path}")
        
        # Preprocess audio
        audio_tensor = preprocess_audio(temp_path)
        print(f"[DEBUG] Audio tensor shape: {audio_tensor.shape}")
        
        audio_tensor = audio_tensor.to(device)
        print(f"[DEBUG] Moved to device: {device}")
        
        # Run inference
        with torch.no_grad():
            # Model returns (hidden_features, output_logits)
            # output_logits shape: [batch_size, 2] where [fake_score, real_score]
            _, output = model(audio_tensor)
            print(f"[DEBUG] Model output: {output}")
            
            # Get scores for fake and real
            fake_score = output[0, 0].item()
            real_score = output[0, 1].item()
            score = real_score - fake_score  # Difference score
        
        # Interpret result
        # Higher score = real, Lower score = fake
        prediction = "real" if score > 0 else "fake"
        
        # Calculate confidence (0-1)
        # Use sigmoid to convert score to probability
        confidence = torch.sigmoid(torch.tensor(score)).item()
        if prediction == "fake":
            confidence = 1 - confidence
        
        # Generate transcript using Whisper
        transcript = ""
        if whisper_model is not None:
            try:
                print("[DEBUG] Generating transcript...")
                result = whisper_model.transcribe(temp_path)
                transcript = result["text"].strip()
                print(f"[DEBUG] Transcript: {transcript}")
            except Exception as e:
                print(f"[WARNING] Transcript generation failed: {e}")
                transcript = "[Transcript unavailable]"
        
        # Clean up temp file
        os.remove(temp_path)
        
        return PredictionResponse(
            filename=file.filename,
            prediction=prediction,
            confidence=float(confidence),
            score=float(score),
            transcript=transcript
        )
    
    except Exception as e:
        # Print full traceback for debugging
        import traceback
        print(f"[ERROR] Exception occurred: {str(e)}")
        print(traceback.format_exc())
        
        # Clean up temp file if it exists
        if temp_path and os.path.exists(temp_path):
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


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time audio streaming
    
    Client can send:
    - Binary audio data (raw PCM float32, 16kHz)
    - JSON with base64 encoded audio
    
    Server responds with JSON predictions
    """
    await websocket.accept()
    client_info = f"{websocket.client.host}:{websocket.client.port}" if websocket.client else "unknown"
    print(f"[WebSocket] Client connected: {client_info}")
    
    audio_buffer = []
    chunk_id = 0
    SAMPLE_RATE = 16000
    CHUNK_SIZE = 32000  # 2 seconds at 16kHz
    
    try:
        while True:
            data = await websocket.receive()
            
            if "bytes" in data:
                # Binary audio data (raw PCM float32)
                raw_audio = data["bytes"]
                audio_chunk = np.frombuffer(raw_audio, dtype=np.float32)
                audio_buffer.extend(audio_chunk)
                
                # Process when we have enough samples
                if len(audio_buffer) >= CHUNK_SIZE:
                    chunk = np.array(audio_buffer[:CHUNK_SIZE])
                    audio_buffer = audio_buffer[CHUNK_SIZE:]
                    
                    # Preprocess and predict
                    audio_tensor = preprocess_audio_array(chunk)
                    audio_tensor = audio_tensor.to(device)
                    
                    with torch.no_grad():
                        _, output = model(audio_tensor)
                        fake_score = output[0, 0].item()
                        real_score = output[0, 1].item()
                        score = real_score - fake_score
                    
                    prediction = "real" if score > 0 else "fake"
                    confidence = torch.sigmoid(torch.tensor(score)).item()
                    if prediction == "fake":
                        confidence = 1 - confidence
                    
                    # Generate transcript
                    transcript = ""
                    if whisper_model is not None:
                        try:
                            # Save chunk to temp file for Whisper
                            temp_path = f"/tmp/ws_chunk_{chunk_id}.wav"
                            sf.write(temp_path, chunk, SAMPLE_RATE)
                            result_whisper = whisper_model.transcribe(temp_path)
                            transcript = result_whisper["text"].strip()
                            os.remove(temp_path)
                        except Exception as e:
                            print(f"[WARNING] Transcript generation failed: {e}")
                            transcript = ""
                    
                    result = {
                        "prediction": prediction,
                        "confidence": float(confidence),
                        "score": float(score),
                        "chunk_id": chunk_id,
                        "buffer_size": len(audio_buffer),
                        "transcript": transcript
                    }
                    
                    await websocket.send_json(result)
                    chunk_id += 1
            
            elif "text" in data:
                # JSON message
                message = json.loads(data["text"])
                
                if message.get("command") == "clear_buffer":
                    audio_buffer = []
                    await websocket.send_json({"status": "buffer_cleared"})
                
                elif message.get("command") == "get_status":
                    await websocket.send_json({
                        "buffer_size": len(audio_buffer),
                        "chunk_id": chunk_id,
                        "model_loaded": model is not None
                    })
                
                elif "audio" in message:
                    # Base64 encoded audio
                    audio_bytes = base64.b64decode(message["audio"])
                    audio_chunk, sr = sf.read(io.BytesIO(audio_bytes))
                    
                    # Convert to mono if stereo
                    if len(audio_chunk.shape) > 1:
                        audio_chunk = np.mean(audio_chunk, axis=1)
                    
                    # Resample if needed (simple)
                    if sr != SAMPLE_RATE:
                        audio_chunk = audio_chunk[::int(sr/SAMPLE_RATE)]
                    
                    # Process
                    audio_tensor = preprocess_audio_array(audio_chunk)
                    audio_tensor = audio_tensor.to(device)
                    
                    with torch.no_grad():
                        _, output = model(audio_tensor)
                        fake_score = output[0, 0].item()
                        real_score = output[0, 1].item()
                        score = real_score - fake_score
                    
                    prediction = "real" if score > 0 else "fake"
                    confidence = torch.sigmoid(torch.tensor(score)).item()
                    if prediction == "fake":
                        confidence = 1 - confidence
                    
                    # Generate transcript
                    transcript = ""
                    if whisper_model is not None:
                        try:
                            # Save chunk to temp file for Whisper
                            temp_path = f"/tmp/ws_chunk_b64_{chunk_id}.wav"
                            sf.write(temp_path, audio_chunk, SAMPLE_RATE)
                            result_whisper = whisper_model.transcribe(temp_path)
                            transcript = result_whisper["text"].strip()
                            os.remove(temp_path)
                        except Exception as e:
                            print(f"[WARNING] Transcript generation failed: {e}")
                            transcript = ""
                    
                    result = {
                        "prediction": prediction,
                        "confidence": float(confidence),
                        "score": float(score),
                        "chunk_id": chunk_id,
                        "transcript": transcript
                    }
                    
                    await websocket.send_json(result)
                    chunk_id += 1
    
    except WebSocketDisconnect:
        print(f"[WebSocket] Client disconnected: {client_info}")
    except Exception as e:
        print(f"[WebSocket] Error: {e}")
        import traceback
        traceback.print_exc()
        try:
            await websocket.send_json({"error": str(e)})
        except:
            pass


def preprocess_audio_array(audio: np.ndarray, max_len: int = 64600) -> torch.Tensor:
    """
    Preprocess numpy audio array for model input
    
    Args:
        audio: Audio samples as numpy array
        max_len: Maximum length for padding
    
    Returns:
        Preprocessed audio tensor
    """
    # Pad or truncate
    audio = pad(audio, max_len=max_len)
    
    # Convert to tensor
    audio_tensor = torch.FloatTensor(audio).unsqueeze(0)
    
    return audio_tensor


@app.get("/web", response_class=HTMLResponse)
async def web_interface():
    """Web interface for audio upload and real-time streaming"""
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Deepfake Audio Detection</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            font-size: 2em;
            margin-bottom: 10px;
        }
        .header p {
            opacity: 0.9;
        }
        .content {
            padding: 30px;
        }
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 2px solid #e0e0e0;
        }
        .tab {
            padding: 15px 30px;
            cursor: pointer;
            border: none;
            background: none;
            font-size: 16px;
            color: #666;
            border-bottom: 3px solid transparent;
            transition: all 0.3s;
        }
        .tab.active {
            color: #667eea;
            border-bottom-color: #667eea;
            font-weight: 600;
        }
        .tab:hover {
            color: #667eea;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        .upload-area {
            border: 3px dashed #ddd;
            border-radius: 15px;
            padding: 40px;
            text-align: center;
            transition: all 0.3s;
            cursor: pointer;
            margin-bottom: 20px;
        }
        .upload-area:hover, .upload-area.dragover {
            border-color: #667eea;
            background: #f8f9ff;
        }
        .upload-icon {
            font-size: 48px;
            margin-bottom: 15px;
        }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            font-size: 16px;
            border-radius: 10px;
            cursor: pointer;
            transition: transform 0.2s;
            font-weight: 600;
            margin: 5px;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }
        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }
        .status {
            padding: 15px;
            margin: 15px 0;
            border-radius: 10px;
            font-weight: 500;
        }
        .status.connected {
            background: #d4edda;
            color: #155724;
            border-left: 4px solid #28a745;
        }
        .status.disconnected {
            background: #f8d7da;
            color: #721c24;
            border-left: 4px solid #dc3545;
        }
        .status.recording {
            background: #fff3cd;
            color: #856404;
            border-left: 4px solid #ffc107;
        }
        .result {
            padding: 20px;
            margin: 10px 0;
            border-radius: 10px;
            animation: slideIn 0.3s ease-out;
        }
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        .result.real {
            background: #d4edda;
            border-left: 4px solid #28a745;
        }
        .result.fake {
            background: #f8d7da;
            border-left: 4px solid #dc3545;
        }
        .result-header {
            font-size: 1.5em;
            font-weight: 700;
            margin-bottom: 10px;
        }
        .result.real .result-header {
            color: #155724;
        }
        .result.fake .result-header {
            color: #721c24;
        }
        .result-details {
            font-size: 0.95em;
            opacity: 0.8;
        }
        .confidence-bar {
            height: 8px;
            background: #e0e0e0;
            border-radius: 4px;
            overflow: hidden;
            margin: 10px 0;
        }
        .confidence-fill {
            height: 100%;
            transition: width 0.5s ease-out;
        }
        .result.real .confidence-fill {
            background: #28a745;
        }
        .result.fake .confidence-fill {
            background: #dc3545;
        }
        #results {
            max-height: 400px;
            overflow-y: auto;
            padding: 10px 0;
        }
        .recording-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            background: #dc3545;
            border-radius: 50%;
            animation: pulse 1.5s ease-in-out infinite;
            margin-right: 8px;
        }
        @keyframes pulse {
            0%, 100% {
                opacity: 1;
            }
            50% {
                opacity: 0.3;
            }
        }
        input[type="file"] {
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎤 Deepfake Audio Detection</h1>
            <p>Powered by AASIST-L Model</p>
        </div>
        
        <div class="content">
            <div class="tabs">
                <button class="tab active" onclick="switchTab('upload')">📁 Upload File</button>
                <button class="tab" onclick="switchTab('stream')">🎙️ Live Stream</button>
            </div>
            
            <!-- Upload Tab -->
            <div id="upload-tab" class="tab-content active">
                <div class="upload-area" id="dropZone" onclick="document.getElementById('fileInput').click()">
                    <div class="upload-icon">📤</div>
                    <h3>Drop WAV file here or click to upload</h3>
                    <p style="color: #666; margin-top: 10px;">Supports .wav files up to 10MB</p>
                </div>
                <input type="file" id="fileInput" accept=".wav" onchange="uploadFile(this.files[0])">
                <div style="text-align: center;">
                    <button onclick="document.getElementById('fileInput').click()">Choose File</button>
                </div>
            </div>
            
            <!-- Stream Tab -->
            <div id="stream-tab" class="tab-content">
                <div id="wsStatus" class="status disconnected">Status: Not connected</div>
                <div style="text-align: center; margin: 20px 0;">
                    <button id="startBtn" onclick="startRecording()">🎙️ Start Recording</button>
                    <button id="stopBtn" onclick="stopRecording()" disabled>⏹️ Stop Recording</button>
                    <button onclick="clearResults()">🗑️ Clear Results</button>
                </div>
                <p style="text-align: center; color: #666; font-size: 0.9em;">
                    Click "Start Recording" to analyze audio from your microphone in real-time
                </p>
            </div>
            
            <div id="results"></div>
        </div>
    </div>

    <script>
        const API_URL = window.location.origin;
        const WS_URL = `ws://${window.location.host}/ws`;
        let ws = null;
        let audioContext = null;
        let processor = null;
        let mediaStream = null;

        // Tab switching
        function switchTab(tab) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            if (tab === 'upload') {
                document.querySelector('.tab:nth-child(1)').classList.add('active');
                document.getElementById('upload-tab').classList.add('active');
            } else {
                document.querySelector('.tab:nth-child(2)').classList.add('active');
                document.getElementById('stream-tab').classList.add('active');
                connectWebSocket();
            }
        }

        // Drag and drop
        const dropZone = document.getElementById('dropZone');
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });
        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('dragover');
        });
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            const file = e.dataTransfer.files[0];
            if (file && file.name.endsWith('.wav')) {
                uploadFile(file);
            } else {
                alert('Please upload a WAV file');
            }
        });

        // Upload file
        async function uploadFile(file) {
            if (!file) return;
            
            const formData = new FormData();
            formData.append('file', file);
            
            try {
                const response = await fetch(`${API_URL}/predict`, {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                displayResult(result, file.name);
            } catch (error) {
                alert('Error: ' + error.message);
            }
        }

        // WebSocket connection
        function connectWebSocket() {
            if (ws && ws.readyState === WebSocket.OPEN) return;
            
            ws = new WebSocket(WS_URL);
            
            ws.onopen = () => {
                updateStatus('Connected', 'connected');
            };
            
            ws.onmessage = (event) => {
                const result = JSON.parse(event.data);
                displayResult(result);
            };
            
            ws.onclose = () => {
                updateStatus('Disconnected', 'disconnected');
            };
            
            ws.onerror = (error) => {
                updateStatus('Error: ' + error, 'disconnected');
            };
        }

        // Start recording
        async function startRecording() {
            try {
                mediaStream = await navigator.mediaDevices.getUserMedia({ 
                    audio: {
                        sampleRate: 16000,
                        channelCount: 1
                    }
                });
                
                audioContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
                const source = audioContext.createMediaStreamSource(mediaStream);
                
                // Buffer size must be power of 2: 256, 512, 1024, 2048, 4096, 8192, or 16384
                // Using 16384 (largest allowed) for best performance
                processor = audioContext.createScriptProcessor(16384, 1, 1);
                
                processor.onaudioprocess = (e) => {
                    if (ws && ws.readyState === WebSocket.OPEN) {
                        const audioData = e.inputBuffer.getChannelData(0);
                        const buffer = new Float32Array(audioData);
                        ws.send(buffer.buffer);
                    }
                };
                
                source.connect(processor);
                processor.connect(audioContext.destination);
                
                document.getElementById('startBtn').disabled = true;
                document.getElementById('stopBtn').disabled = false;
                updateStatus('<span class="recording-indicator"></span>Recording...', 'recording');
            } catch (err) {
                alert('Microphone error: ' + err.message);
            }
        }

        // Stop recording
        function stopRecording() {
            if (processor) {
                processor.disconnect();
                processor = null;
            }
            if (audioContext) {
                audioContext.close();
                audioContext = null;
            }
            if (mediaStream) {
                mediaStream.getTracks().forEach(track => track.stop());
                mediaStream = null;
            }
            
            document.getElementById('startBtn').disabled = false;
            document.getElementById('stopBtn').disabled = true;
            updateStatus('Connected', 'connected');
        }

        // Display result
        function displayResult(result, filename) {
            const resultsDiv = document.getElementById('results');
            const resultClass = result.prediction === 'real' ? 'real' : 'fake';
            const emoji = result.prediction === 'real' ? '✅' : '⚠️';
            const confidence = (result.confidence * 100).toFixed(1);
            const transcript = result.transcript || '';
            
            const resultHtml = `
                <div class="result ${resultClass}">
                    <div class="result-header">
                        ${emoji} ${result.prediction.toUpperCase()}
                    </div>
                    <div class="confidence-bar">
                        <div class="confidence-fill" style="width: ${confidence}%"></div>
                    </div>
                    <div class="result-details">
                        <strong>Confidence:</strong> ${confidence}%
                        <br>
                        <strong>Score:</strong> ${result.score.toFixed(3)}
                        ${filename ? `<br><strong>File:</strong> ${filename}` : ''}
                        ${result.chunk_id !== undefined ? `<br><strong>Chunk:</strong> #${result.chunk_id}` : ''}
                        ${transcript ? `<br><br><strong>📝 Transcript:</strong><br><em>"${transcript}"</em>` : ''}
                    </div>
                </div>
            `;
            
            resultsDiv.innerHTML = resultHtml + resultsDiv.innerHTML;
        }

        // Update status
        function updateStatus(message, type) {
            const statusDiv = document.getElementById('wsStatus');
            statusDiv.innerHTML = 'Status: ' + message;
            statusDiv.className = 'status ' + type;
        }

        // Clear results
        function clearResults() {
            document.getElementById('results').innerHTML = '';
        }
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)


if __name__ == "__main__":
    import uvicorn
    
    # Load model
    load_model()
    
    # Run server
    print("\n🚀 Starting Deepfake Audio Detection API...")
    print("📖 Interactive docs: http://localhost:8000/docs")
    print("🌐 Web interface: http://localhost:8000/web")
    print("📡 WebSocket: ws://localhost:8000/ws")
    uvicorn.run(app, host="0.0.0.0", port=8000)
