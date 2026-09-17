import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiService } from '../services/api';

// Detection Sessions
export const useSessions = () => {
  return useQuery({ queryKey: ['sessions'], queryFn: () => apiService.getSessions() });
};

export const useSession = (id: string) => {
  return useQuery({ queryKey: ['sessions', id], queryFn: () => apiService.getSession(id), enabled: !!id });
};

// Logs
export const useLogs = (params?: any) => {
  return useQuery({ queryKey: ['logs', params], queryFn: () => apiService.getLogs(params) });
};

export const useLogStats = (params?: any) => {
  return useQuery({ queryKey: ['logs', 'stats', params], queryFn: () => apiService.getLogStats(params) });
};

export const useLogDistribution = (params?: any) => {
  return useQuery({ queryKey: ['logs', 'distribution', params], queryFn: () => apiService.getLogDistribution(params) });
};

// Models
export const useModels = () => {
  return useQuery({ queryKey: ['models'], queryFn: () => apiService.getModels() });
};

export const useUploadModel = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (formData: FormData) => apiService.uploadModel(formData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['models'] });
    }
  });
};

export const useActivateModel = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => apiService.activateModel(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['models'] });
      queryClient.invalidateQueries({ queryKey: ['inferenceInfo'] });
    }
  });
};

// Varieties
export const useVarieties = () => {
  return useQuery({ queryKey: ['varieties'], queryFn: () => apiService.getVarieties() });
};

// Settings
export const useSettings = () => {
  return useQuery({ queryKey: ['settings'], queryFn: () => apiService.getSettings() });
};

// Performance
export const useSystemMetrics = (refetchInterval = 0) => {
  return useQuery({ 
    queryKey: ['systemMetrics'], 
    queryFn: () => apiService.getSystemMetrics(),
    refetchInterval 
  });
};

export const useInferenceInfo = () => {
  return useQuery({ queryKey: ['inferenceInfo'], queryFn: () => apiService.getInferenceInfo() });
};
