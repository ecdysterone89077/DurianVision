
from pydantic import BaseModel


class BoundingBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float
    w: float
    h: float

class DetectionBox(BaseModel):
    class_id: int
    class_name: str
    confidence: float
    bbox: BoundingBox

class PredictRequest(BaseModel):
    confidence: float = 0.5
    iou: float = 0.45
    imgsz: int = 640

class PredictResponse(BaseModel):
    detections: list[DetectionBox]
    inference_time_ms: float
    frame_number: int | None = None
    model_name: str

class ModelInfo(BaseModel):
    path: str
    device: str
    classes: list[str]
    is_loaded: bool
    framework: str

class LoadModelRequest(BaseModel):
    model_path: str

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    device: str
    gpu_available: bool

class SystemMetrics(BaseModel):
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    gpu_name: str | None = None
    gpu_utilization: float | None = None
    gpu_memory_used_mb: float | None = None
