import { getSystemMetrics as sidecarMetrics, getModelInfo as sidecarModelInfo, getHealth } from './inference.service.js';
import { updateSettings } from './settings.service.js';

export const getSystemMetrics = async () => {
  try {
    return await sidecarMetrics();
  } catch (error) {
    return { error: 'Failed to fetch metrics from inference service' };
  }
};

export const getInferenceInfo = async () => {
  try {
    const [info, health] = await Promise.all([
      sidecarModelInfo(),
      getHealth()
    ]);
    return { ...info, status: health.status };
  } catch (error) {
    return { status: 'offline' };
  }
};

export const updateConfig = async (config: { fpsLimit?: number; inferenceSize?: number; device?: string }) => {
  return await updateSettings(config);
};
