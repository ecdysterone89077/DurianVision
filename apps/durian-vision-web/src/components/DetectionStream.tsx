import { useEffect, useRef, useState, useCallback } from 'react';
import { socket } from '../lib/socket';
import { useSettings } from '../hooks/use-queries';
import { apiService } from '../services/api';

interface DetectionStreamProps {
  sessionId: string;
  isActive: boolean;
  onInferenceTime?: (time: number) => void;
}

export default function DetectionStream({ sessionId, isActive, onInferenceTime }: DetectionStreamProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const { data: settings } = useSettings();
  const [streamActive, setStreamActive] = useState(false);
  const lastSnapshotRef = useRef(0);
  
  const fpsLimit = settings?.fpsLimit || 5;
  const intervalRef = useRef<number | null>(null);

  // Setup Webcam
  useEffect(() => {
    let isMounted = true;
    let currentStream: MediaStream | null = null;

    const initCamera = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
          video: { facingMode: 'environment', width: { ideal: 1280 }, height: { ideal: 720 } } 
        });
        if (!isMounted) {
          stream.getTracks().forEach(t => t.stop());
          return;
        }
        currentStream = stream;
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          videoRef.current.play();
          setStreamActive(true);
        }
      } catch (err) {
        console.error("Camera error:", err);
      }
    };
    initCamera();

    return () => {
      isMounted = false;
      if (currentStream) {
        currentStream.getTracks().forEach(t => t.stop());
      }
    };
  }, []);

  const drawDetections = useCallback((detections: any[]) => {
    const canvas = canvasRef.current;
    const video = videoRef.current;
    if (!canvas || !video) return;
    if (video.videoWidth === 0 || video.videoHeight === 0) return;

    // Match canvas size to video container size
    canvas.width = video.clientWidth;
    canvas.height = video.clientHeight;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Calculate actual video dimensions inside the object-fit: contain box
    const videoRatio = video.videoWidth / video.videoHeight;
    const containerRatio = canvas.width / canvas.height;
    
    let renderWidth, renderHeight, offsetX = 0, offsetY = 0;
    
    if (containerRatio > videoRatio) {
      // Container is wider than video (Black bars on left/right)
      renderHeight = canvas.height;
      renderWidth = canvas.height * videoRatio;
      offsetX = (canvas.width - renderWidth) / 2;
    } else {
      // Container is taller than video (Black bars on top/bottom)
      renderWidth = canvas.width;
      renderHeight = canvas.width / videoRatio;
      offsetY = (canvas.height - renderHeight) / 2;
    }

    // Scaling factors from intrinsic video to actual rendered video size
    const scaleX = renderWidth / video.videoWidth;
    const scaleY = renderHeight / video.videoHeight;

    detections.forEach(d => {
      const { x1, y1, x2, y2 } = d.bbox;
      const width = (x2 - x1) * scaleX;
      const height = (y2 - y1) * scaleY;
      
      // Add offsets to align with object-fit: contain rendering
      const x = (x1 * scaleX) + offsetX;
      const y = (y1 * scaleY) + offsetY;

      // Draw Box
      ctx.strokeStyle = '#4be277'; // Primary color
      ctx.lineWidth = settings?.boxThickness || 2;
      ctx.strokeRect(x, y, width, height);

      // Draw Label Background
      ctx.fillStyle = 'rgba(75, 226, 119, 0.2)';
      ctx.fillRect(x, y, width, height);
      
      // Draw Label Text
      if (settings?.showLabels !== false) {
        const text = `${d.class_name} ${Math.round(d.confidence * 100)}%`;
        ctx.fillStyle = '#4be277';
        ctx.font = `bold ${settings?.fontSize || 14}px monospace`;
        const textWidth = ctx.measureText(text).width;
        
        ctx.fillRect(x, y - 20, textWidth + 10, 20);
        ctx.fillStyle = '#0a100d'; // on-primary
        ctx.fillText(text, x + 5, y - 5);
      }
    });
  }, [settings]);

  const maybeAutoSnapshot = useCallback((detections: any[]) => {
    if (!settings?.autoSnapshot || !detections || detections.length === 0) return;
    const intervalMs = (settings?.autoSnapshotInterval ?? 30) * 1000;
    const now = Date.now();
    if (now - lastSnapshotRef.current < intervalMs) return;
    const video = videoRef.current;
    if (!video || !video.videoWidth) return;
    lastSnapshotRef.current = now;

    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d')?.drawImage(video, 0, 0);
    canvas.toBlob(async (blob) => {
      if (!blob) return;
      const form = new FormData();
      form.append('file', blob, `snapshot_${now}.jpg`);
      form.append('sessionId', sessionId);
      form.append('detections', JSON.stringify(detections));
      form.append('metadata', JSON.stringify({ source: 'web', device_type: 'webcam' }));
      try {
        await apiService.uploadSnapshot(form);
      } catch (e) {
        console.error('[DetectionStream] Auto snapshot failed:', e);
      }
    }, 'image/jpeg', 0.9);
  }, [settings, sessionId]);

  // Socket Connection and Frame Loop
  useEffect(() => {
    const handleConnect = () => {
      console.log('[DetectionStream] Socket connected:', socket.id);
      socket.emit('join-session', sessionId);
    };

    const handleConnectError = (err: any) => {
      console.error('[DetectionStream] Socket connection error:', err.message);
    };

    socket.on('connect', handleConnect);
    socket.on('connect_error', handleConnectError);

    const handleDetection = (data: any) => {
      if (onInferenceTime) onInferenceTime(data.inferenceTimeMs);
      drawDetections(data.detections);
      maybeAutoSnapshot(data.detections);
    };

    socket.on('detection-result', handleDetection);

    if (!socket.connected) {
      socket.connect();
    } else {
      socket.emit('join-session', sessionId);
    }

    return () => {
      socket.emit('leave-session', sessionId);
      socket.off('detection-result', handleDetection);
      socket.off('connect', handleConnect);
      socket.off('connect_error', handleConnectError);
    };
  }, [sessionId, onInferenceTime, drawDetections, maybeAutoSnapshot]);

  // Frame Capture Loop
  useEffect(() => {
    if (!isActive || !streamActive) {
      if (intervalRef.current) window.clearInterval(intervalRef.current);
      return;
    }

    const captureFrame = () => {
      if (!videoRef.current || !canvasRef.current) return;
      
      const video = videoRef.current;
      const canvas = document.createElement('canvas');
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext('2d');
      if (!ctx) return;

      ctx.drawImage(video, 0, 0);
      canvas.toBlob((blob) => {
        if (!blob) return;
        socket.emit('process-frame', {
          sessionId,
          image: blob, // Socket.io automatically converts File/Blob to ArrayBuffer binary
          config: { 
            confidence: settings?.confidenceThreshold || 0.5,
            iou: settings?.iouThreshold ?? 0.45,
            imgsz: settings?.inferenceSize || 640 
          }
        });
      }, 'image/jpeg', 1.0);
    };

    intervalRef.current = window.setInterval(captureFrame, 1000 / fpsLimit);

    return () => {
      if (intervalRef.current) window.clearInterval(intervalRef.current);
    };
  }, [isActive, streamActive, fpsLimit, settings, sessionId]);

  return (
    <div className="relative w-full h-full bg-surface-dim overflow-hidden flex items-center justify-center">
      {!streamActive && (
        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none opacity-50 gap-sm">
          <span className="material-symbols-outlined text-[48px] animate-pulse">videocam</span>
          <span className="font-mono-data">INITIALIZING CAMERA...</span>
        </div>
      )}
      
      {/* Video Feed */}
      <video 
        ref={videoRef} 
        className="max-w-full max-h-full object-contain"
        playsInline 
        muted 
      />
      
      {/* Bounding Box Overlay */}
      <canvas 
        ref={canvasRef} 
        className="absolute inset-0 w-full h-full pointer-events-none" 
        style={{ objectFit: 'contain' }}
      />
    </div>
  );
}
