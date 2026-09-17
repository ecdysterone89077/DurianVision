import { useState, useRef } from 'react';
import { useModels, useUploadModel, useActivateModel } from '../hooks/use-queries';

export default function ModelManager() {
  const { data: models, isLoading } = useModels();
  const uploadMutation = useUploadModel();
  const activateMutation = useActivateModel();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleUpload(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleUpload(e.target.files[0]);
    }
  };

  const handleUpload = (file: File) => {
    if (!file.name.endsWith('.pt')) {
      alert('Only .pt YOLO model files are supported');
      return;
    }
    const formData = new FormData();
    formData.append('file', file);
    formData.append('name', file.name.replace('.pt', ''));
    uploadMutation.mutate(formData);
  };

  return (
    <div className="bg-surface-container p-lg rounded-xl border border-outline-variant flex flex-col gap-lg shadow-sm">
      <div className="flex items-center gap-sm border-b border-surface-container-highest pb-sm">
        <span className="material-symbols-outlined text-secondary" style={{ fontVariationSettings: "'FILL' 1" }}>model_training</span>
        <h2 className="font-headline-sm text-headline-sm text-on-surface">AI Model Weights</h2>
      </div>
      
      {/* Active & Available Models */}
      <div className="flex flex-col gap-sm">
        {isLoading ? (
          <div className="animate-pulse h-10 bg-surface-dim rounded-md"></div>
        ) : (
          models?.map((model: any) => (
            <div key={model.id} className={`flex items-center justify-between p-sm rounded-md border ${model.isActive ? 'border-primary bg-primary/5' : 'border-outline-variant bg-surface-dim'}`}>
              <div className="flex flex-col">
                <span className={`font-body-sm text-body-sm ${model.isActive ? 'text-primary font-bold' : 'text-on-surface'}`}>{model.filename}</span>
                <span className="font-mono-data text-[10px] text-on-surface-variant">{(model.fileSize / 1024 / 1024).toFixed(1)} MB</span>
              </div>
              {!model.isActive && (
                <button 
                  onClick={() => activateMutation.mutate(model.id)}
                  disabled={activateMutation.isPending}
                  className="px-3 py-1 bg-surface-container-high hover:bg-surface-bright text-on-surface text-sm rounded-md transition-colors"
                >
                  Activate
                </button>
              )}
              {model.isActive && (
                <span className="px-2 py-1 bg-primary/20 text-primary text-[10px] rounded-sm font-mono-data border border-primary/30">ACTIVE</span>
              )}
            </div>
          ))
        )}
      </div>

      {/* Upload Zone */}
      <div 
        className={`border-2 border-dashed rounded-lg p-md text-center transition-colors cursor-pointer flex flex-col items-center justify-center gap-sm ${isDragging ? 'border-primary bg-primary/5' : 'border-outline hover:border-on-surface-variant'}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input 
          type="file" 
          accept=".pt" 
          className="hidden" 
          ref={fileInputRef} 
          onChange={handleFileSelect} 
        />
        <span className={`material-symbols-outlined text-3xl ${isDragging ? 'text-primary' : 'text-on-surface-variant'}`}>cloud_upload</span>
        <div className="flex flex-col">
          <span className="font-body-sm text-on-surface">Drop your <span className="font-mono-data">.pt</span> model file here</span>
          <span className="font-mono-data text-[10px] text-on-surface-variant">or click to browse</span>
        </div>
        {uploadMutation.isPending && (
          <div className="mt-2 text-primary font-mono-data text-[10px] animate-pulse">Uploading...</div>
        )}
      </div>
    </div>
  );
}
