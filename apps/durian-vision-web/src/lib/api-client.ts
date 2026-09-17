import axios from 'axios';

export const apiClient = axios.create({
  baseURL: `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:3005'}/api`,
  withCredentials: true,
});

apiClient.interceptors.response.use(
  (response) => {
    const res = response.data;
    if (res && typeof res === 'object' && 'success' in res && 'data' in res) {
      if (res.meta) {
        return { data: res.data, meta: res.meta } as any;
      }
      return res.data as any;
    }
    return res as any;
  },
  (error) => {
    return Promise.reject(error.response?.data || error);
  }
);

// Type override to prevent AxiosResponse wrapper
const client: Record<string, any> = {
  get: (url: string, config?: any) => apiClient.get(url, config).then(res => res as any),
  post: (url: string, data?: any, config?: any) => apiClient.post(url, data, config).then(res => res as any),
  patch: (url: string, data?: any, config?: any) => apiClient.patch(url, data, config).then(res => res as any),
  delete: (url: string, config?: any) => apiClient.delete(url, config).then(res => res as any),
};

export { client as typedApiClient };
