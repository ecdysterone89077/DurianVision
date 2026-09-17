import { typedApiClient as apiClient } from '../lib/api-client';

export const apiService = {
  // Detection Sessions
  createSession: (data: any) => apiClient.post('/detection', data),
  getSessions: () => apiClient.get('/detection'),
  getSession: (id: string) => apiClient.get(`/detection/${id}`),
  updateSession: (id: string, data: any) => apiClient.patch(`/detection/${id}`, data),
  deleteSession: (id: string) => apiClient.delete(`/detection/${id}`),
  startSession: (id: string) => apiClient.post(`/detection/${id}/start`),
  stopSession: (id: string) => apiClient.post(`/detection/${id}/stop`),
  pauseSession: (id: string) => apiClient.post(`/detection/${id}/pause`),

  // Logs
  getLogs: (params?: any) => apiClient.get('/logs', { params }),
  getLogStats: (params?: any) => apiClient.get('/logs/stats', { params }),
  getLogDistribution: (params?: any) => apiClient.get('/logs/distribution', { params }),
  clearLogs: (params?: any) => apiClient.delete('/logs', { params }),
  exportCSV: (params?: any) => apiClient.get('/logs/export/csv', { params, responseType: 'blob' }),
  exportXLSX: (params?: any) => apiClient.get('/logs/export/xlsx', { params, responseType: 'blob' }),
  
  // Snapshots
  getSnapshots: (params?: any) => apiClient.get('/snapshots', { params }),
  getSnapshot: (id: string) => apiClient.get(`/snapshots/${id}`),
  deleteSnapshot: (id: string) => apiClient.delete(`/snapshots/${id}`),

  // Models
  getModels: () => apiClient.get('/models'),
  getModel: (id: string) => apiClient.get(`/models/${id}`),
  uploadModel: (formData: FormData) => apiClient.post('/models/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  activateModel: (id: string) => apiClient.patch(`/models/${id}/activate`),
  deleteModel: (id: string) => apiClient.delete(`/models/${id}`),

  // Performance / System
  getSystemMetrics: () => apiClient.get('/performance/system'),
  getInferenceInfo: () => apiClient.get('/performance/inference'),
  updateConfig: (data: any) => apiClient.patch('/performance/config', data),

  // Varieties
  getVarieties: () => apiClient.get('/varieties'),
  getVariety: (id: string) => apiClient.get(`/varieties/${id}`),
  createVariety: (data: any) => apiClient.post('/varieties', data),
  updateVariety: (id: string, data: any) => apiClient.patch(`/varieties/${id}`, data),
  deleteVariety: (id: string) => apiClient.delete(`/varieties/${id}`),

  // Settings
  getSettings: () => apiClient.get('/settings'),
  updateSettings: (data: any) => apiClient.patch('/settings', data),
  resetSettings: () => apiClient.post('/settings/reset'),
};
