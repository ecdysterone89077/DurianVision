import { useState } from 'react';
import { useLogs, useLogStats } from '../hooks/use-queries';
import { apiService } from '../services/api';

export default function Log() {
  const [page, setPage] = useState(1);
  const limit = 20;
  const { data: logData, isLoading, refetch } = useLogs({ page, limit });
  const { data: stats } = useLogStats();

  const handleExportCSV = async () => {
    try {
      const res = await apiService.exportCSV();
      const url = window.URL.createObjectURL(new Blob([res as any]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'logs.csv');
      document.body.appendChild(link);
      link.click();
      window.URL.revokeObjectURL(url);
      link.remove();
    } catch (e) {
      console.error('Failed to export CSV', e);
    }
  };

  const handleExportXLSX = async () => {
    try {
      const res = await apiService.exportXLSX();
      const url = window.URL.createObjectURL(new Blob([res as any]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'logs.xlsx');
      document.body.appendChild(link);
      link.click();
      window.URL.revokeObjectURL(url);
      link.remove();
    } catch (e) {
      console.error('Failed to export XLSX', e);
    }
  };

  const handleClear = async () => {
    if (confirm('Are you sure you want to delete all logs?')) {
      await apiService.clearLogs();
      refetch();
    }
  };

  const logs = Array.isArray(logData) ? logData : (logData?.data || []);
  const totalLogs = logData?.meta?.total || 0;
  const totalPages = Math.ceil(totalLogs / limit);

  return (
    <>
      <header className="bg-surface-dim dark:bg-surface-dim flex justify-between items-center w-full px-lg py-sm z-10 border-b border-surface-container-highest shadow-md hidden md:flex">
        <div>
          <h2 className="font-headline-sm text-headline-sm font-bold text-primary dark:text-primary">Detection Log &amp; Analytics</h2>
        </div>
      </header>

      <div className="flex-grow p-lg overflow-y-auto pb-xl">
        <div className="grid grid-cols-12 gap-lg max-w-container-max mx-auto h-full grid-rows-[auto_1fr]">
          
          <div className="col-span-12 glass-panel rounded-xl flex flex-col overflow-hidden min-h-[400px]">
            <div className="p-md border-b border-[#334155] flex justify-between items-center bg-surface-container-low flex-wrap gap-sm">
              <div className="flex items-center gap-sm">
                <span className="material-symbols-outlined text-primary">history</span>
                <h3 className="font-headline-sm text-headline-sm text-on-surface">Detection History</h3>
                <span className="bg-surface-dim px-2 py-1 rounded text-on-surface-variant font-mono-data text-[12px] border border-outline-variant">{totalLogs} records</span>
              </div>
              <div className="flex gap-sm">
                <button onClick={handleExportCSV} className="px-md py-xs rounded border border-[#334155] text-on-surface hover:border-primary hover:text-primary transition-colors font-label-caps text-label-caps flex items-center gap-xs">
                  <span className="material-symbols-outlined text-[16px]">download</span>
                  CSV
                </button>
                <button onClick={handleExportXLSX} className="px-md py-xs rounded border border-[#334155] text-on-surface hover:border-primary hover:text-primary transition-colors font-label-caps text-label-caps flex items-center gap-xs">
                  <span className="material-symbols-outlined text-[16px]">table</span>
                  XLSX
                </button>
                <button onClick={handleClear} className="px-md py-xs rounded border border-error/50 text-error hover:bg-error-container transition-colors font-label-caps text-label-caps flex items-center gap-xs ml-md">
                  <span className="material-symbols-outlined text-[16px]">delete</span>
                  Clear
                </button>
              </div>
            </div>
            
            <div className="flex-grow overflow-auto relative">
              {isLoading && (
                <div className="absolute inset-0 bg-background/50 flex items-center justify-center z-20 backdrop-blur-[2px]">
                  <span className="material-symbols-outlined animate-spin text-primary text-4xl">refresh</span>
                </div>
              )}
              <table className="w-full text-left border-collapse min-w-[600px]">
                <thead className="sticky top-0 bg-[#0F172A] z-10 border-b border-[#334155]">
                  <tr>
                    <th className="p-md font-label-caps text-label-caps text-on-surface-variant">Time</th>
                    <th className="p-md font-label-caps text-label-caps text-on-surface-variant">Session ID</th>
                    <th className="p-md font-label-caps text-label-caps text-on-surface-variant">Variety</th>
                    <th className="p-md font-label-caps text-label-caps text-on-surface-variant">Confidence</th>
                    <th className="p-md font-label-caps text-label-caps text-on-surface-variant">BBox (X, Y)</th>
                  </tr>
                </thead>
                <tbody className="font-mono-data text-mono-data text-on-surface">
                  {logs.length === 0 && !isLoading && (
                    <tr>
                      <td colSpan={5} className="p-xl text-center text-on-surface-variant">No detection logs found.</td>
                    </tr>
                  )}
                  {logs.map((log: any, i: number) => (
                    <tr key={log.id} className={`border-b border-[#334155] hover:bg-surface-variant transition-colors ${i % 2 === 0 ? 'bg-[#1E293B]' : 'bg-[#0F172A]'}`}>
                      <td className="p-md text-on-surface-variant">{new Date(log.detectedAt).toLocaleString()}</td>
                      <td className="p-md text-on-surface-variant text-[10px] truncate max-w-[100px]">{log.sessionId}</td>
                      <td className="p-md">{log.variety}</td>
                      <td className="p-md">
                        <span className={log.confidence >= 0.8 ? 'text-primary font-bold' : log.confidence >= 0.5 ? 'text-tertiary' : 'text-error'}>
                          {(log.confidence * 100).toFixed(1)}%
                        </span>
                      </td>
                      <td className="p-md text-on-surface-variant text-[12px]">
                        [{log.bboxX}, {log.bboxY}, {log.bboxW}, {log.bboxH}]
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <div className="p-md border-t border-[#334155] bg-surface-container-low flex justify-between items-center">
              <span className="font-body-sm text-on-surface-variant">Showing page {page} of {totalPages || 1}</span>
              <div className="flex gap-sm">
                <button 
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page <= 1}
                  className="px-sm py-xs bg-surface-dim border border-outline-variant rounded disabled:opacity-50 hover:bg-surface-variant transition-colors"
                >
                  Prev
                </button>
                <button 
                  onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                  disabled={page >= totalPages}
                  className="px-sm py-xs bg-surface-dim border border-outline-variant rounded disabled:opacity-50 hover:bg-surface-variant transition-colors"
                >
                  Next
                </button>
              </div>
            </div>
          </div>
          
          <div className="col-span-12 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-md mt-md">
            <div className="glass-panel p-md rounded-xl border border-primary/20 flex flex-col gap-sm relative overflow-hidden">
              <div className="absolute top-0 right-0 p-sm text-primary/10">
                <span className="material-symbols-outlined text-[64px]">dataset</span>
              </div>
              <h4 className="font-label-caps text-label-caps text-on-surface-variant z-10">Total Detections</h4>
              <span className="font-headline-lg text-headline-lg text-on-surface z-10">{stats?.total || 0}</span>
            </div>
            
            <div className="glass-panel p-md rounded-xl border border-secondary/20 flex flex-col gap-sm relative overflow-hidden">
              <div className="absolute top-0 right-0 p-sm text-secondary/10">
                <span className="material-symbols-outlined text-[64px]">check_circle</span>
              </div>
              <h4 className="font-label-caps text-label-caps text-on-surface-variant z-10">Avg Confidence</h4>
              <span className="font-headline-lg text-headline-lg text-secondary z-10">
                {stats?.avgConfidence ? (stats.avgConfidence * 100).toFixed(1) : 0}%
              </span>
            </div>

            <div className="glass-panel p-md rounded-xl border border-tertiary/20 flex flex-col gap-sm relative overflow-hidden">
              <h4 className="font-label-caps text-label-caps text-on-surface-variant z-10 mb-xs">Top Varieties</h4>
              <div className="flex gap-md z-10 flex-wrap">
                {stats?.byVariety?.slice(0, 3).map((dist: any) => (
                  <div key={dist.name} className="flex-1 bg-surface-dim border border-outline-variant rounded p-sm flex flex-col">
                    <span className="font-body-sm text-on-surface mb-xs">{dist.name}</span>
                    <span className="font-mono-data text-primary text-lg">{dist.count}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

        </div>
      </div>
    </>
  );
}
