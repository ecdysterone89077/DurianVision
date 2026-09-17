import ModelManager from '../components/ModelManager';
import { useSystemMetrics, useSettings } from '../hooks/use-queries';
import { useState, useEffect, useRef } from 'react';
import { apiService } from '../services/api';

export default function Performance() {
  const { data: metrics } = useSystemMetrics(2000);
  const { data: settings } = useSettings();
  
  const [fps, setFps] = useState(5);
  const [inferenceSize, setInferenceSize] = useState(640);
  const debounceRef = useRef<number>(undefined);
  
  useEffect(() => {
    if (settings) {
      setFps(settings.fpsLimit || 5);
      setInferenceSize(settings.inferenceSize || 640);
    }
  }, [settings]);

  const handleFpsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = parseInt(e.target.value);
    setFps(val);
    clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      apiService.updateSettings({ fpsLimit: val });
    }, 500);
  };

  const handleSizeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const val = parseInt(e.target.value);
    setInferenceSize(val);
    apiService.updateSettings({ inferenceSize: val });
  };

  return (
    <>
      <div className="md:hidden flex justify-between items-center w-full px-lg py-sm bg-surface-dim dark:bg-surface-dim border-b border-surface-container-low z-40">
        <div className="flex items-center gap-sm">
          <span className="font-headline-sm text-headline-sm font-bold text-primary dark:text-primary">DurianVision v1.0</span>
        </div>
        <div className="flex items-center gap-sm">
          <span className="material-symbols-outlined text-on-surface-variant text-xl cursor-pointer hover:text-primary transition-colors">menu</span>
        </div>
      </div>

      <div className="flex-1 flex flex-col h-full overflow-y-auto overflow-x-hidden relative pb-[60px] md:pb-0">
        <div className="px-md md:px-lg py-lg border-b border-surface-container-highest bg-surface/80 backdrop-blur-md sticky top-0 z-20">
          <h1 className="font-headline-lg text-headline-lg text-on-surface mb-xs">System Performance</h1>
          <p className="font-body-sm text-body-sm text-on-surface-variant">Resource allocation and inference configuration.</p>
        </div>
        
        <div className="p-md md:p-lg grid grid-cols-1 lg:grid-cols-12 gap-md max-w-container-max mx-auto w-full">
          <div className="lg:col-span-7 flex flex-col gap-md">
            
            <ModelManager />
            
            <div className="bg-surface-container p-lg rounded-xl border border-outline-variant flex flex-col gap-lg shadow-sm">
              <div className="flex items-center gap-sm border-b border-surface-container-highest pb-sm">
                <span className="material-symbols-outlined text-secondary" style={{ fontVariationSettings: "'FILL' 1" }}>tune</span>
                <h2 className="font-headline-sm text-headline-sm text-on-surface">Inference Resolution</h2>
              </div>
              <div className="flex flex-col gap-xs">
                <label className="font-label-caps text-label-caps text-on-surface-variant">Input Resolution</label>
                <div className="relative">
                  <select 
                    value={inferenceSize} 
                    onChange={handleSizeChange}
                    className="w-full bg-surface-dim border border-outline-variant rounded-md py-sm px-md text-on-surface font-body-sm appearance-none focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors cursor-pointer"
                  >
                    <option value="320">320x320 (Fastest)</option>
                    <option value="416">416x416 (Smartphone)</option>
                    <option value="640">640x640 (Desktop Default)</option>
                  </select>
                  <span className="material-symbols-outlined absolute right-md top-1/2 -translate-y-1/2 text-on-surface-variant pointer-events-none">expand_more</span>
                </div>
              </div>
            </div>
            
            <div className="bg-surface-container p-lg rounded-xl border border-outline-variant flex flex-col gap-lg shadow-sm">
              <div className="flex items-center justify-between border-b border-surface-container-highest pb-sm">
                <div className="flex items-center gap-sm">
                  <span className="material-symbols-outlined text-tertiary" style={{ fontVariationSettings: "'FILL' 1" }}>speed</span>
                  <h2 className="font-headline-sm text-headline-sm text-on-surface">Framerate Limiter</h2>
                </div>
                <span className="font-mono-data text-mono-data text-tertiary bg-tertiary/10 px-sm py-[2px] rounded-sm border border-tertiary/30">{fps} FPS</span>
              </div>
              <div className="flex flex-col gap-md pt-sm">
                <div className="flex justify-between font-mono-data text-mono-data text-on-surface-variant text-[10px]">
                  <span>1 FPS</span>
                  <span>15 FPS</span>
                  <span>30 FPS</span>
                  <span>60 FPS</span>
                </div>
                <input 
                  className="w-full h-2 bg-surface-container-highest rounded-lg appearance-none cursor-pointer accent-primary" 
                  max="60" min="1" type="range" 
                  value={fps} 
                  onChange={handleFpsChange} 
                />
              </div>
            </div>
          </div>
          
          <div className="lg:col-span-5 flex flex-col gap-md">
            <div className="bg-surface-container p-lg rounded-xl border border-outline-variant shadow-sm h-full flex flex-col">
              <div className="flex items-center gap-sm mb-lg">
                <div className="w-2 h-2 rounded-full bg-primary animate-pulse"></div>
                <h2 className="font-headline-sm text-headline-sm text-on-surface">Live Telemetry</h2>
              </div>
              <div className="flex flex-col gap-lg flex-1 justify-center">
                <div className="flex flex-col gap-xs">
                  <div className="flex justify-between items-end">
                    <span className="font-label-caps text-label-caps text-on-surface-variant">CPU Core Load</span>
                    <span className="font-mono-data text-mono-data text-on-surface">{metrics?.cpu_percent?.toFixed(1) || 0}%</span>
                  </div>
                  <div className="w-full bg-surface-container-highest rounded-full h-2 overflow-hidden">
                    <div className="bg-primary h-2 rounded-full glow-active transition-all" style={{ width: `${metrics?.cpu_percent || 0}%` }}></div>
                  </div>
                </div>
                <div className="flex flex-col gap-xs">
                  <div className="flex justify-between items-end">
                    <span className="font-label-caps text-label-caps text-on-surface-variant">RAM Used</span>
                    <span className="font-mono-data text-mono-data text-on-surface">{metrics?.memory_percent?.toFixed(1) || 0}%</span>
                  </div>
                  <div className="w-full bg-surface-container-highest rounded-full h-2 overflow-hidden">
                    <div className="bg-secondary h-2 rounded-full transition-all" style={{ width: `${metrics?.memory_percent || 0}%`, boxShadow: '0 0 8px 0 rgba(173, 198, 255, 0.2)' }}></div>
                  </div>
                </div>
                {metrics?.gpu_name && (
                  <div className="flex flex-col gap-xs">
                    <div className="flex justify-between items-end">
                      <span className="font-label-caps text-label-caps text-on-surface-variant">GPU: {metrics.gpu_name}</span>
                      <span className="font-mono-data text-mono-data text-tertiary">{metrics.gpu_utilization?.toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-surface-container-highest rounded-full h-2 overflow-hidden">
                      <div className="bg-tertiary h-2 rounded-full transition-all" style={{ width: `${metrics.gpu_utilization || 0}%`, boxShadow: '0 0 8px 0 rgba(247, 191, 30, 0.2)' }}></div>
                    </div>
                  </div>
                )}
              </div>
            </div>
            
          </div>
        </div>
      </div>
      
      <footer className="fixed bottom-0 left-0 w-full z-50 flex justify-between items-center px-lg py-xs bg-surface-container-highest dark:bg-surface-container-highest border-t border-outline-variant/30 md:pl-[calc(16rem+24px)] pointer-events-none">
        <div className="font-mono-data text-mono-data text-primary truncate max-w-[50%] flex items-center gap-sm pointer-events-auto">
          <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse shrink-0"></span>
          DurianVision Connected
        </div>
      </footer>
    </>
  );
}
