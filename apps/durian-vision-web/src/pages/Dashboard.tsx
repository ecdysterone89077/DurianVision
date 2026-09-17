import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useSessions, useModels, useLogDistribution, useSystemMetrics, useInferenceInfo } from '../hooks/use-queries';
import { apiService } from '../services/api';
import DetectionStream from '../components/DetectionStream';

export default function Dashboard() {
  const { data: sessions, refetch: refetchSessions } = useSessions();
  const { data: models } = useModels();
  const activeModel = models?.find((m: any) => m.isActive);

  const { data: distribution } = useLogDistribution();
  const { data: sysMetrics } = useSystemMetrics(10000);
  const { data: inferenceInfo } = useInferenceInfo();

  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [isDetecting, setIsDetecting] = useState(false);
  const [inferenceTime, setInferenceTime] = useState<number>(0);

  // Auto-create or get latest active session
  useEffect(() => {
    const initSession = async () => {
      if (sessions === undefined) return;
      if (sessions && sessions.length > 0) {
        setActiveSessionId(sessions[0].id);
        setIsDetecting(sessions[0].status === 'running');
      } else {
        const newSession = await apiService.createSession({ status: 'idle', deviceType: 'smartphone' });
        setActiveSessionId(newSession.id);
        refetchSessions();
      }
    };
    initSession();
  }, [sessions, refetchSessions]);

  const handleStart = async () => {
    if (!activeSessionId) return;
    await apiService.startSession(activeSessionId);
    setIsDetecting(true);
    refetchSessions();
  };

  const handlePause = async () => {
    if (!activeSessionId) return;
    await apiService.pauseSession(activeSessionId);
    setIsDetecting(false);
    refetchSessions();
  };

  return (
    <>
      <div className="md:hidden flex justify-between items-center w-full px-lg py-sm bg-surface-dim dark:bg-surface-dim border-b border-surface-container-low z-20">
        <div className="flex items-center gap-sm">
          <span className="font-headline-sm text-headline-sm font-bold text-primary dark:text-primary">DurianVision v1.0</span>
        </div>
        <div className="flex gap-sm">
          <span className="material-symbols-outlined text-on-surface-variant hover:bg-surface-variant dark:hover:bg-surface-variant transition-colors p-xs rounded-DEFAULT cursor-pointer" data-icon="close">close</span>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-md lg:p-lg pb-xl">
        <div className="max-w-container-max mx-auto grid grid-cols-1 lg:grid-cols-12 gap-md h-full">
          {/* Left/Main Column: Controls & Monitoring */}
          <div className="lg:col-span-8 flex flex-col gap-md">
            <section className="bg-surface-container border border-outline-variant rounded-lg p-md glass-card ai-border-glow">
              <div className="flex items-center justify-between mb-sm">
                <h2 className="font-label-caps text-label-caps text-primary tracking-wider flex items-center gap-xs">
                  <span className="material-symbols-outlined text-[16px]">tune</span>
                  DETECTION CONTROL
                </h2>
                <div className="flex items-center gap-xs bg-surface-container-highest px-sm py-xs rounded-full border border-outline">
                  <div className={`w-2 h-2 rounded-full ${isDetecting ? 'bg-primary active-pulse' : 'bg-surface-variant'}`}></div>
                  <span className="font-mono-data text-mono-data text-primary text-[11px] uppercase">{isDetecting ? 'Engine Online' : 'Engine Idle'}</span>
                </div>
              </div>
              
              <div className="flex flex-wrap gap-md items-center justify-between">
                <div className="flex gap-sm">
                  {!isDetecting ? (
                    <button onClick={handleStart} className="bg-primary hover:bg-primary-fixed text-on-primary font-label-caps text-label-caps px-lg py-sm rounded-DEFAULT flex items-center gap-xs transition-colors shadow-[0_0_12px_rgba(75,226,119,0.3)]">
                      <span className="material-symbols-outlined text-[18px]" style={{ fontVariationSettings: "'FILL' 1" }}>play_arrow</span>
                      START INFERENCE
                    </button>
                  ) : (
                    <button onClick={handlePause} className="bg-surface-container-high border border-outline-variant hover:bg-surface-bright text-on-surface font-label-caps text-label-caps px-lg py-sm rounded-DEFAULT flex items-center gap-xs transition-colors">
                      <span className="material-symbols-outlined text-[18px]">pause</span>
                      PAUSE
                    </button>
                  )}
                </div>
                <div className="flex gap-lg">
                  <div>
                    <p className="font-label-caps text-label-caps text-on-surface-variant mb-xs">Inference Time</p>
                    <p className="font-mono-data text-mono-data text-on-surface text-lg">{isDetecting ? `${inferenceTime.toFixed(1)} ms` : '-'}</p>
                  </div>
                  <div>
                    <p className="font-label-caps text-label-caps text-on-surface-variant mb-xs">Model Load</p>
                    <p className="font-mono-data text-mono-data text-on-surface text-lg truncate w-24" title={activeModel?.filename}>{activeModel?.filename || 'Loading...'}</p>
                  </div>
                </div>
              </div>
            </section>

            <section className="bg-surface-container border border-outline-variant rounded-lg p-xs glass-card flex-1 flex flex-col min-h-[400px]">
              <div className="p-sm flex justify-between items-center border-b border-outline-variant">
                <h2 className="font-label-caps text-label-caps text-on-surface tracking-wider flex items-center gap-xs">
                  <span className="material-symbols-outlined text-[16px]">visibility</span>
                  AREA MONITORING
                </h2>
                <div className="flex gap-xs">
                  <Link to="/roi" className="p-xs text-on-surface-variant hover:text-primary transition-colors flex items-center">
                    <span className="material-symbols-outlined text-[18px]">crop</span>
                  </Link>
                  <button className="p-xs text-on-surface-variant hover:text-primary transition-colors">
                    <span className="material-symbols-outlined text-[18px]">zoom_in</span>
                  </button>
                  <button className="p-xs text-on-surface-variant hover:text-primary transition-colors">
                    <span className="material-symbols-outlined text-[18px]">fullscreen</span>
                  </button>
                </div>
              </div>
              
              <div className="relative flex-1 bg-surface-dim rounded-b-DEFAULT overflow-hidden m-xs border border-outline-variant flex items-center justify-center">
                {activeSessionId ? (
                  <DetectionStream 
                    sessionId={activeSessionId} 
                    isActive={isDetecting} 
                    onInferenceTime={setInferenceTime} 
                  />
                ) : (
                  <div className="font-mono-data text-on-surface-variant">Loading Session...</div>
                )}
              </div>
            </section>
          </div>

          <div className="lg:col-span-4 flex flex-col gap-md">
            {/* Right Column Content */}
            <section className="bg-surface-container border border-outline-variant rounded-lg p-md glass-card">
              <div className="flex justify-between items-center mb-sm">
                <h2 className="font-label-caps text-label-caps text-on-surface tracking-wider">LIVE DISTRIBUTION</h2>
              </div>
              <div className="flex flex-col gap-sm">
                {distribution && distribution.length > 0 ? (
                  distribution.map((d: any) => (
                    <div key={d.name} className="flex justify-between items-center p-sm bg-surface-dim rounded border border-outline-variant">
                      <span className="font-body-sm text-on-surface">{d.name}</span>
                      <span className="font-mono-data text-primary">{d.percentage?.toFixed(1)}%</span>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-sm text-on-surface-variant font-body-sm">No detection data yet</div>
                )}
              </div>
            </section>
          </div>
        </div>
      </div>
      
      <footer className="bg-surface-container-highest dark:bg-surface-container-highest fixed bottom-0 left-0 w-full z-50 flex justify-between items-center px-lg py-xs border-t border-surface-variant shadow-[0_-4px_24px_rgba(0,0,0,0.5)] md:pl-[calc(16rem+24px)] pointer-events-none">
        <div className="font-mono-data text-mono-data text-primary flex items-center gap-sm pointer-events-auto">
          <span className="w-2 h-2 rounded-full bg-primary active-pulse"></span>
          Detection {isDetecting ? 'Active' : 'Idle'} | CPU {sysMetrics?.cpu_percent != null ? `${Math.round(sysMetrics.cpu_percent)}%` : '--'} | RAM {sysMetrics?.memory_percent != null ? `${Math.round(sysMetrics.memory_percent)}%` : '--'} | {String(inferenceInfo?.device || 'CPU').toUpperCase()} | API v1.0
        </div>
        <div className="hidden md:flex gap-lg pointer-events-auto">
          <a className="font-mono-data text-mono-data text-tertiary dark:text-tertiary-fixed-dim hover:text-primary transition-colors opacity-70" href="#">System Logs</a>
          <a className="font-mono-data text-mono-data text-tertiary dark:text-tertiary-fixed-dim hover:text-primary transition-colors opacity-70" href="#">Network Status</a>
          <a className="font-mono-data text-mono-data text-tertiary dark:text-tertiary-fixed-dim hover:text-primary transition-colors opacity-70" href="#">API v2.1</a>
        </div>
      </footer>
    </>
  );
}
