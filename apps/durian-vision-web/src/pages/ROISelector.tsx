import { useEffect, useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useSessions } from '../hooks/use-queries';
import { apiService } from '../services/api';

interface Rect {
  x: number;
  y: number;
  w: number;
  h: number;
}

const detectDevice = (w: number, h: number) => {
  const ratio = Math.max(w, h) / Math.max(1, Math.min(w, h));
  if (h > w || ratio < 1.2) {
    return { type: 'Smartphone', aspect: `${w}:${h}`, fps: 5, imgsz: 416 };
  }
  return { type: 'Desktop', aspect: ratio <= 1.8 ? '16:9' : 'Ultrawide', fps: 10, imgsz: 640 };
};

export default function ROISelector() {
  const navigate = useNavigate();
  const { data: sessions, refetch } = useSessions();
  const videoRef = useRef<HTMLVideoElement>(null);
  const [streamActive, setStreamActive] = useState(false);
  const [dragging, setDragging] = useState(false);
  const [rect, setRect] = useState<Rect | null>(null);
  const [intrinsic, setIntrinsic] = useState<Rect | null>(null);
  const [saving, setSaving] = useState(false);

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
        console.error('Camera error:', err);
      }
    };
    initCamera();

    return () => {
      isMounted = false;
      if (currentStream) currentStream.getTracks().forEach(t => t.stop());
    };
  }, []);

  const videoRect = () => videoRef.current?.getBoundingClientRect() ?? null;

  const toDisplay = (clientX: number, clientY: number) => {
    const r = videoRect();
    if (!r) return { x: 0, y: 0, w: 0, h: 0 };
    return {
      x: Math.min(Math.max(0, clientX - r.left), r.width),
      y: Math.min(Math.max(0, clientY - r.top), r.height),
      w: 0,
      h: 0
    };
  };

  const handlePointerDown = (e: React.PointerEvent<HTMLVideoElement>) => {
    const pt = toDisplay(e.clientX, e.clientY);
    setRect({ x: pt.x, y: pt.y, w: 0, h: 0 });
    setDragging(true);
    e.currentTarget.setPointerCapture(e.pointerId);
  };

  const handlePointerMove = (e: React.PointerEvent<HTMLVideoElement>) => {
    if (!dragging) return;
    const r = videoRect();
    if (!r) return;
    const x = Math.min(Math.max(0, e.clientX - r.left), r.width);
    const y = Math.min(Math.max(0, e.clientY - r.top), r.height);
    setRect(prev => {
      if (!prev) return prev;
      return { x: Math.min(prev.x, x), y: Math.min(prev.y, y), w: Math.abs(x - prev.x), h: Math.abs(y - prev.y) };
    });
  };

  const handlePointerUp = () => {
    setDragging(false);
    const video = videoRef.current;
    const box = videoRect();
    if (!video || !box || box.width === 0) return;
    setRect(prev => {
      if (!prev || prev.w < 10 || prev.h < 10) {
        setIntrinsic(null);
        return prev;
      }
      const scale = video.videoWidth / box.width;
      setIntrinsic({
        x: Math.round(prev.x * scale),
        y: Math.round(prev.y * scale),
        w: Math.round(prev.w * scale),
        h: Math.round(prev.h * scale)
      });
      return prev;
    });
  };

  const device = intrinsic && intrinsic.w > 0 ? detectDevice(intrinsic.w, intrinsic.h) : null;

  const handleFullscreen = () => {
    const video = videoRef.current;
    const box = videoRect();
    if (!video || !box) return;
    setRect({ x: 0, y: 0, w: box.width, h: box.height });
    setIntrinsic({ x: 0, y: 0, w: video.videoWidth, h: video.videoHeight });
  };

  const handleConfirm = async () => {
    if (!intrinsic || intrinsic.w < 10 || intrinsic.h < 10 || !device) return;
    setSaving(true);
    try {
      let sessionId = sessions?.[0]?.id;
      if (!sessionId) {
        const created = await apiService.createSession({ status: 'idle', deviceType: device.type.toLowerCase() });
        sessionId = created.id;
      }
      await apiService.updateSession(sessionId, {
        roiX: intrinsic.x,
        roiY: intrinsic.y,
        roiWidth: intrinsic.w,
        roiHeight: intrinsic.h,
        deviceType: device.type.toLowerCase(),
        aspectRatio: device.aspect,
        fpsLimit: device.fps,
        inferenceSize: device.imgsz
      });
      refetch();
      navigate('/dashboard');
    } catch (e) {
      console.error('Gagal menyimpan ROI:', e);
      setSaving(false);
    }
  };

  return (
    <div className="bg-background text-on-surface font-body-md h-screen w-full overflow-hidden flex flex-col antialiased">
      <header className="bg-surface-dim text-primary flex justify-between items-center w-full px-lg py-sm relative z-50">
        <div className="font-headline-sm text-headline-sm font-bold text-primary flex items-center gap-sm">
          <span className="material-symbols-outlined" data-icon="precision_manufacturing">precision_manufacturing</span>
          DurianVision v1.0
        </div>
        <div className="hidden"></div>
        <div className="flex items-center gap-md">
          <Link to="/dashboard" aria-label="Close" className="hover:bg-error-container hover:text-on-error-container transition-colors rounded p-xs text-on-surface-variant block">
            <span className="material-symbols-outlined" data-icon="close">close</span>
          </Link>
        </div>
      </header>

      <main className="relative flex-grow w-full h-full bg-surface-container-lowest flex items-center justify-center overflow-hidden">
        {!streamActive && (
          <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none opacity-50 gap-sm z-10">
            <span className="material-symbols-outlined text-[48px] animate-pulse">videocam</span>
            <span className="font-mono-data">INITIALIZING CAMERA...</span>
          </div>
        )}

        <div className="relative inline-flex max-w-full max-h-full">
          <video
            ref={videoRef}
            className="max-w-full max-h-full block object-contain cursor-crosshair select-none"
            playsInline
            muted
            onPointerDown={handlePointerDown}
            onPointerMove={handlePointerMove}
            onPointerUp={handlePointerUp}
          />

          {rect && rect.w > 0 && rect.h > 0 && (
            <div
              className="absolute border-2 border-primary pointer-events-none"
              style={{ left: rect.x, top: rect.y, width: rect.w, height: rect.h }}
            >
              <span className="absolute -bottom-6 left-0 bg-surface-container-high/90 text-primary font-mono-data text-mono-data px-xs rounded">
                {intrinsic ? `${intrinsic.w}x${intrinsic.h}px` : ''}
              </span>
            </div>
          )}
        </div>

        <div className="absolute top-lg right-lg z-20">
          <div className="bg-surface-container/90 border border-outline-variant rounded-lg p-md backdrop-blur-md shadow-[0_4px_24px_rgba(0,0,0,0.5)] flex flex-col gap-sm min-w-[320px]">
            <div className="flex items-center gap-sm border-b border-surface-container-highest pb-xs mb-xs">
              <span className="material-symbols-outlined text-tertiary" data-icon="tune">tune</span>
              <h3 className="font-label-caps text-label-caps text-on-surface tracking-wider">Region of Interest</h3>
            </div>
            <div className="grid grid-cols-1 gap-xs font-mono-data text-mono-data">
              <div className="flex justify-between items-center bg-surface-container-low p-xs rounded">
                <span className="text-on-surface-variant flex items-center gap-xs">
                  <span className="material-symbols-outlined text-[16px]" data-icon="smartphone">smartphone</span> Device:
                </span>
                <span className="text-on-surface">{device ? device.type : 'Belum dipilih'}</span>
              </div>
              <div className="flex justify-between items-center bg-surface-container-low p-xs rounded">
                <span className="text-on-surface-variant flex items-center gap-xs">
                  <span className="material-symbols-outlined text-[16px]" data-icon="aspect_ratio">aspect_ratio</span> Resolution:
                </span>
                <span className="text-on-surface">{intrinsic ? `${intrinsic.w}x${intrinsic.h}px` : '-'}</span>
              </div>
              <div className="flex justify-between items-center bg-surface-container-low p-xs rounded">
                <span className="text-on-surface-variant flex items-center gap-xs">
                  <span className="material-symbols-outlined text-[16px]" data-icon="speed">speed</span> Auto FPS:
                </span>
                <span className="text-primary font-bold">{device ? device.fps : '-'}</span>
              </div>
            </div>
            <p className="font-body-sm text-on-surface-variant text-[11px]">Klik dan seret pada video untuk memilih area pemantauan.</p>
          </div>
        </div>
      </main>

      <div className="absolute bottom-xl left-1/2 -translate-x-1/2 z-20 flex gap-md bg-surface-container-high/90 p-xs rounded-full backdrop-blur-md border border-outline-variant">
        <Link to="/dashboard" className="px-lg py-sm rounded-full font-label-caps text-label-caps bg-surface-container-low text-on-surface hover:bg-surface-variant hover:text-primary transition-colors flex items-center gap-xs">
          <span className="material-symbols-outlined text-[18px]" data-icon="close">close</span>
          Cancel
        </Link>
        <button onClick={handleFullscreen} className="px-lg py-sm rounded-full font-label-caps text-label-caps bg-surface-container-low text-on-surface hover:bg-surface-variant hover:text-primary transition-colors flex items-center gap-xs">
          <span className="material-symbols-outlined text-[18px]" data-icon="fullscreen">fullscreen</span>
          Full Screen
        </button>
        <button
          onClick={handleConfirm}
          disabled={!intrinsic || saving}
          className="px-lg py-sm rounded-full font-label-caps text-label-caps bg-primary text-on-primary hover:bg-primary-fixed transition-colors flex items-center gap-xs shadow-[0_0_12px_rgba(75,226,119,0.3)] disabled:opacity-40"
        >
          <span className="material-symbols-outlined text-[18px]" data-icon="check">check</span>
          {saving ? 'Menyimpan...' : 'Confirm'}
        </button>
      </div>

      <footer className="bg-surface-container-highest text-tertiary font-mono-data text-mono-data fixed bottom-0 left-0 w-full z-50 flex justify-between items-center px-lg py-xs border-t-0">
        <div className="flex items-center gap-sm">
          <span className="w-2 h-2 rounded-full bg-primary animate-pulse shadow-[0_0_8px_rgba(75,226,119,0.8)]"></span>
          ROI Selector | Kamera: <span className="text-primary">{streamActive ? 'aktif' : 'tidak tersedia'}</span> | Area: <span className="text-primary">{intrinsic ? `${intrinsic.w}x${intrinsic.h}` : 'belum dipilih'}</span>
        </div>
        <div className="flex gap-md">
          <Link className="text-on-surface-variant hover:text-primary transition-colors" to="/log">System Logs</Link>
          <Link className="text-on-surface-variant hover:text-primary transition-colors" to="/performance">Network Status</Link>
          <span className="text-on-surface-variant">API v1.0</span>
        </div>
      </footer>
    </div>
  );
}
