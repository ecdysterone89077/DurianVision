import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiService } from '../services/api';

export default function Snapshot() {
  const queryClient = useQueryClient();
  const { data: snapshots, isLoading } = useQuery({
    queryKey: ['snapshots'],
    queryFn: () => apiService.getSnapshots(),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => apiService.deleteSnapshot(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['snapshots'] }),
  });

  const items = Array.isArray(snapshots) ? snapshots : (snapshots?.data || []);

  return (
    <>
      <header className="bg-surface-dim dark:bg-surface-dim flex justify-between items-center w-full px-lg py-sm z-10 border-b border-surface-container-highest shadow-md hidden md:flex">
        <div>
          <h2 className="font-headline-sm text-headline-sm font-bold text-primary dark:text-primary">Snapshot Gallery</h2>
        </div>
      </header>

      <div className="flex-grow p-lg overflow-y-auto pb-xl">
        <div className="max-w-container-max mx-auto">
          {isLoading && (
            <div className="flex items-center justify-center py-xl">
              <span className="material-symbols-outlined animate-spin text-primary text-4xl">refresh</span>
            </div>
          )}

          {!isLoading && items.length === 0 && (
            <div className="flex flex-col items-center justify-center py-xl text-on-surface-variant gap-sm">
              <span className="material-symbols-outlined text-[64px] opacity-30">photo_camera</span>
              <p className="font-body-sm">No snapshots yet. Detections will appear here.</p>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-md">
            {items.map((snap: any) => (
              <div key={snap.id} className="glass-panel rounded-xl border border-outline-variant overflow-hidden flex flex-col">
                <div className="aspect-video bg-surface-dim flex items-center justify-center overflow-hidden">
                  {snap.url ? (
                    <img
                      src={`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:3005'}${snap.url}`}
                      alt={snap.filename}
                      className="w-full h-full object-cover"
                      loading="lazy"
                    />
                  ) : (
                    <span className="material-symbols-outlined text-[48px] text-on-surface-variant opacity-30">image</span>
                  )}
                </div>
                <div className="p-md flex flex-col gap-xs">
                  <div className="flex justify-between items-center">
                    <span className="font-label-caps text-label-caps text-on-surface-variant">
                      {snap.numDetections || 0} detections
                    </span>
                    <span className="font-mono-data text-mono-data text-on-surface-variant text-[10px]">
                      {snap.createdAt ? new Date(snap.createdAt).toLocaleString() : '-'}
                    </span>
                  </div>
                  <div className="flex gap-sm mt-xs">
                    {snap.url && (
                      <a
                        href={`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:3005'}/api/snapshots/${snap.id}/download`}
                        className="flex-1 text-center px-sm py-xs rounded border border-outline-variant text-on-surface hover:border-primary hover:text-primary transition-colors font-label-caps text-label-caps flex items-center justify-center gap-xs"
                      >
                        <span className="material-symbols-outlined text-[14px]">download</span>
                        Download
                      </a>
                    )}
                    <button
                      onClick={() => deleteMutation.mutate(snap.id)}
                      className="px-sm py-xs rounded border border-error/50 text-error hover:bg-error-container transition-colors font-label-caps text-label-caps flex items-center gap-xs"
                    >
                      <span className="material-symbols-outlined text-[14px]">delete</span>
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}
