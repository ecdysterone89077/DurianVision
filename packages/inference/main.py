import base64
import binascii

import cv2
import numpy as np
import psutil
import torch
import uvicorn
from engine import YOLOv11Engine
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from schemas import (
    DetectionBox,
    HealthResponse,
    LoadModelRequest,
    ModelInfo,
    PredictResponse,
    SystemMetrics,
)

app = FastAPI(title="DurianVision Inference Sidecar")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3005", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = YOLOv11Engine(model_path='models/best.pt', device='auto')

class Base64PredictRequest(BaseModel):
    image: str
    confidence: float = 0.5
    iou: float = 0.45
    imgsz: int = 640

@app.on_event("startup")
async def startup_event():
    pass

def _decode_image_from_bytes(image_bytes: bytes) -> np.ndarray:
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Failed to decode image")
    return img

@app.post("/predict", response_model=PredictResponse)
async def predict(
    file: UploadFile = File(...),
    confidence: float = Form(0.5),
    iou: float = Form(0.45),
    imgsz: int = Form(640)
):
    try:
        contents = await file.read()
        if len(contents) > 20_000_000:
            raise HTTPException(400, 'File too large (max 20MB)')
        img = _decode_image_from_bytes(contents)
        
        detections, inference_time_ms = await run_in_threadpool(engine.predict, img, conf=confidence, iou=iou, imgsz=imgsz)
        
        return PredictResponse(
            detections=[DetectionBox(**d) for d in detections],
            inference_time_ms=inference_time_ms,
            model_name="yolov11"
        )
    except (ValueError, binascii.Error) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/base64", response_model=PredictResponse)
def predict_base64(request: Base64PredictRequest):
    try:
        if "," in request.image:
            img_data = request.image.split(",")[1]
        else:
            img_data = request.image
            
        img_bytes = base64.b64decode(img_data)
        img = _decode_image_from_bytes(img_bytes)
        
        detections, inference_time_ms = engine.predict(
            img, conf=request.confidence, iou=request.iou, imgsz=request.imgsz
        )
        
        return PredictResponse(
            detections=[DetectionBox(**d) for d in detections],
            inference_time_ms=inference_time_ms,
            model_name="yolov11"
        )
    except (ValueError, binascii.Error) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/load-model")
def load_model(request: LoadModelRequest):
    import os
    if not os.path.realpath(request.model_path).startswith(os.path.realpath('models/')):
        raise HTTPException(status_code=400, detail="Invalid model path")
    success = engine.load_model(request.model_path)
    if not success:
        raise HTTPException(status_code=400, detail=f"Failed to load model from {request.model_path}")
    return {"status": "success", "message": f"Loaded model from {request.model_path}"}

@app.post("/reload-model")
def reload_model():
    success = engine.load_model('models/best.pt')
    if not success:
        raise HTTPException(status_code=400, detail="Failed to reload models/best.pt")
    return {"status": "success", "message": "Reloaded models/best.pt"}

@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="ok",
        model_loaded=engine.is_loaded,
        device=engine.get_model_info()["device"],
        gpu_available=torch.cuda.is_available()
    )

@app.get("/model-info", response_model=ModelInfo)
async def get_model_info():
    info = engine.get_model_info()
    return ModelInfo(**info)

@app.get("/system-metrics", response_model=SystemMetrics)
async def system_metrics():
    mem = psutil.virtual_memory()
    metrics = {
        "cpu_percent": psutil.cpu_percent(interval=None),
        "memory_percent": mem.percent,
        "memory_used_mb": mem.used / (1024 * 1024),
        "gpu_name": None,
        "gpu_utilization": None,
        "gpu_memory_used_mb": None
    }
    
    if torch.cuda.is_available():
        try:
            metrics["gpu_name"] = torch.cuda.get_device_name(0)
            metrics["gpu_memory_used_mb"] = torch.cuda.memory_allocated(0) / (1024 * 1024)
            try:
                import pynvml
                pynvml.nvmlInit()
                try:
                    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                    util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                    metrics["gpu_utilization"] = float(util.gpu)
                finally:
                    pynvml.nvmlShutdown()
            except ImportError:
                pass
        except Exception:
            pass
            
    return SystemMetrics(**metrics)

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8001, reload=True)
