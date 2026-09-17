const INFERENCE_URL = process.env.INFERENCE_URL || 'http://localhost:8001';

export const predict = async (imageBuffer: Buffer, config?: { confidence?: number; iou?: number; imgsz?: number }) => {
  const formData = new FormData();
  formData.append('file', new Blob([imageBuffer], { type: 'image/jpeg' }), 'image.jpg');
  if (config?.confidence !== undefined) {
    formData.append('confidence', String(config.confidence));
  }
  if (config?.iou !== undefined) {
    formData.append('iou', String(config.iou));
  }
  if (config?.imgsz !== undefined) {
    formData.append('imgsz', String(config.imgsz));
  }

  const res = await fetch(`${INFERENCE_URL}/predict`, {
    method: 'POST',
    body: formData
  });
  if (!res.ok) throw new Error('Inference failed');
  return await res.json();
};

export const predictBase64 = async (base64: string, config?: { confidence?: number; iou?: number; imgsz?: number }) => {
  const res = await fetch(`${INFERENCE_URL}/predict/base64`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      image: base64,
      confidence: config?.confidence ?? 0.5,
      iou: config?.iou ?? 0.45,
      imgsz: config?.imgsz ?? 640
    })
  });
  if (!res.ok) throw new Error('Inference failed');
  return await res.json();
};

export const loadModel = async (modelPath: string) => {
  const res = await fetch(`${INFERENCE_URL}/load-model`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ model_path: modelPath })
  });
  if (!res.ok) throw new Error('Failed to load model');
  return await res.json();
};

export const reloadModel = async () => {
  const res = await fetch(`${INFERENCE_URL}/reload-model`, {
    method: 'POST'
  });
  if (!res.ok) throw new Error('Failed to reload model');
  return await res.json();
};

export const getHealth = async () => {
  const res = await fetch(`${INFERENCE_URL}/health`);
  return await res.json();
};

export const getModelInfo = async () => {
  const res = await fetch(`${INFERENCE_URL}/model-info`);
  return await res.json();
};

export const getSystemMetrics = async () => {
  const res = await fetch(`${INFERENCE_URL}/system-metrics`);
  return await res.json();
};
