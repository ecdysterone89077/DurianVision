import { useState, useEffect } from 'react';
import { useSettings } from '../hooks/use-queries';
import { apiService } from '../services/api';

export default function Settings() {
  const { data: settings, refetch } = useSettings();

  const [confidence, setConfidence] = useState(0.5);
  const [iou, setIou] = useState(0.45);
  const [showLabels, setShowLabels] = useState(true);
  const [showConfidence, setShowConfidence] = useState(true);
  const [boxThickness, setBoxThickness] = useState(2);
  const [fontSize, setFontSize] = useState(14);
  const [autoSnapshot, setAutoSnapshot] = useState(false);
  const [autoSnapshotInterval, setAutoSnapshotInterval] = useState(30);

  useEffect(() => {
    if (settings) {
      setConfidence(settings.confidenceThreshold ?? 0.5);
      setIou(settings.iouThreshold ?? 0.45);
      setShowLabels(settings.showLabels ?? true);
      setShowConfidence(settings.showConfidence ?? true);
      setBoxThickness(settings.boxThickness ?? 2);
      setFontSize(settings.fontSize ?? 14);
      setAutoSnapshot(settings.autoSnapshot ?? false);
      setAutoSnapshotInterval(settings.autoSnapshotInterval ?? 30);
    }
  }, [settings]);

  const handleSave = async () => {
    await apiService.updateSettings({
      confidenceThreshold: confidence,
      iouThreshold: iou,
      showLabels,
      showConfidence,
      boxThickness,
      fontSize,
      autoSnapshot,
      autoSnapshotInterval,
    });
    refetch();
  };

  const handleReset = async () => {
    if (confirm('Reset all settings to default?')) {
      await apiService.resetSettings();
      refetch();
    }
  };

  return (
    <>
      <div className="flex-1 flex flex-col h-full overflow-y-auto overflow-x-hidden relative pb-[60px] md:pb-0">
        <div className="px-md md:px-lg py-lg border-b border-surface-container-highest bg-surface/80 backdrop-blur-md sticky top-0 z-20">
          <h1 className="font-headline-lg text-headline-lg text-on-surface mb-xs">Settings</h1>
          <p className="font-body-sm text-body-sm text-on-surface-variant">Detection and overlay configuration.</p>
        </div>

        <div className="p-md md:p-lg grid grid-cols-1 lg:grid-cols-2 gap-md max-w-container-max mx-auto w-full">
          {/* Detection Settings */}
          <div className="bg-surface-container p-lg rounded-xl border border-outline-variant flex flex-col gap-lg shadow-sm">
            <div className="flex items-center gap-sm border-b border-surface-container-highest pb-sm">
              <span className="material-symbols-outlined text-primary" style={{ fontVariationSettings: "'FILL' 1" }}>tune</span>
              <h2 className="font-headline-sm text-headline-sm text-on-surface">Detection Parameters</h2>
            </div>

            <div className="flex flex-col gap-md">
              <div>
                <div className="flex justify-between mb-xs">
                  <label className="font-label-caps text-label-caps text-on-surface-variant">Confidence Threshold</label>
                  <span className="font-mono-data text-mono-data text-primary">{(confidence * 100).toFixed(0)}%</span>
                </div>
                <input
                  className="w-full h-2 bg-surface-container-highest rounded-lg appearance-none cursor-pointer accent-primary"
                  type="range" min="0" max="100" value={Math.round(confidence * 100)}
                  onChange={e => setConfidence(Number(e.target.value) / 100)}
                />
              </div>

              <div>
                <div className="flex justify-between mb-xs">
                  <label className="font-label-caps text-label-caps text-on-surface-variant">IoU Threshold</label>
                  <span className="font-mono-data text-mono-data text-secondary">{(iou * 100).toFixed(0)}%</span>
                </div>
                <input
                  className="w-full h-2 bg-surface-container-highest rounded-lg appearance-none cursor-pointer accent-secondary"
                  type="range" min="0" max="100" value={Math.round(iou * 100)}
                  onChange={e => setIou(Number(e.target.value) / 100)}
                />
              </div>
            </div>
          </div>

          {/* Overlay Settings */}
          <div className="bg-surface-container p-lg rounded-xl border border-outline-variant flex flex-col gap-lg shadow-sm">
            <div className="flex items-center gap-sm border-b border-surface-container-highest pb-sm">
              <span className="material-symbols-outlined text-secondary" style={{ fontVariationSettings: "'FILL' 1" }}>layers</span>
              <h2 className="font-headline-sm text-headline-sm text-on-surface">Overlay Display</h2>
            </div>

            <div className="flex flex-col gap-md">
              <label className="flex items-center justify-between cursor-pointer">
                <span className="font-body-sm text-on-surface">Show Labels</span>
                <input type="checkbox" checked={showLabels} onChange={e => setShowLabels(e.target.checked)} className="accent-primary w-5 h-5" />
              </label>
              <label className="flex items-center justify-between cursor-pointer">
                <span className="font-body-sm text-on-surface">Show Confidence</span>
                <input type="checkbox" checked={showConfidence} onChange={e => setShowConfidence(e.target.checked)} className="accent-primary w-5 h-5" />
              </label>
              <div>
                <div className="flex justify-between mb-xs">
                  <label className="font-label-caps text-label-caps text-on-surface-variant">Box Thickness</label>
                  <span className="font-mono-data text-mono-data text-tertiary">{boxThickness}px</span>
                </div>
                <input
                  className="w-full h-2 bg-surface-container-highest rounded-lg appearance-none cursor-pointer accent-tertiary"
                  type="range" min="1" max="5" value={boxThickness}
                  onChange={e => setBoxThickness(Number(e.target.value))}
                />
              </div>
              <div>
                <div className="flex justify-between mb-xs">
                  <label className="font-label-caps text-label-caps text-on-surface-variant">Font Size</label>
                  <span className="font-mono-data text-mono-data text-tertiary">{fontSize}px</span>
                </div>
                <input
                  className="w-full h-2 bg-surface-container-highest rounded-lg appearance-none cursor-pointer accent-tertiary"
                  type="range" min="10" max="24" value={fontSize}
                  onChange={e => setFontSize(Number(e.target.value))}
                />
              </div>
            </div>
          </div>

          {/* Auto Snapshot */}
          <div className="bg-surface-container p-lg rounded-xl border border-outline-variant flex flex-col gap-lg shadow-sm">
            <div className="flex items-center gap-sm border-b border-surface-container-highest pb-sm">
              <span className="material-symbols-outlined text-tertiary" style={{ fontVariationSettings: "'FILL' 1" }}>photo_camera</span>
              <h2 className="font-headline-sm text-headline-sm text-on-surface">Auto Snapshot</h2>
            </div>
            <label className="flex items-center justify-between cursor-pointer">
              <span className="font-body-sm text-on-surface">Enable Auto Snapshot</span>
              <input type="checkbox" checked={autoSnapshot} onChange={e => setAutoSnapshot(e.target.checked)} className="accent-primary w-5 h-5" />
            </label>
            {autoSnapshot && (
              <div>
                <div className="flex justify-between mb-xs">
                  <label className="font-label-caps text-label-caps text-on-surface-variant">Interval</label>
                  <span className="font-mono-data text-mono-data text-tertiary">{autoSnapshotInterval}s</span>
                </div>
                <input
                  className="w-full h-2 bg-surface-container-highest rounded-lg appearance-none cursor-pointer accent-tertiary"
                  type="range" min="5" max="120" value={autoSnapshotInterval}
                  onChange={e => setAutoSnapshotInterval(Number(e.target.value))}
                />
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="bg-surface-container p-lg rounded-xl border border-outline-variant flex flex-col gap-lg shadow-sm justify-center">
            <button
              onClick={handleSave}
              className="w-full bg-primary hover:bg-primary-fixed text-on-primary font-label-caps text-label-caps px-lg py-sm rounded-DEFAULT flex items-center justify-center gap-xs transition-colors shadow-[0_0_12px_rgba(75,226,119,0.3)]"
            >
              <span className="material-symbols-outlined text-[18px]">save</span>
              Save Settings
            </button>
            <button
              onClick={handleReset}
              className="w-full px-lg py-sm rounded border border-error/50 text-error hover:bg-error-container transition-colors font-label-caps text-label-caps flex items-center justify-center gap-xs"
            >
              <span className="material-symbols-outlined text-[18px]">restart_alt</span>
              Reset to Default
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
