import { Router } from 'express';
import { getSystemMetrics, getInferenceInfo, updateConfig } from '../services/performance.service.js';
import { success } from '../utils/api-response.js';
import { requireAuth } from '../middleware/auth.middleware.js';

const router = Router();

router.use(requireAuth);

router.get('/system', async (req, res, next) => {
  try {
    const data = await getSystemMetrics();
    res.json(success(data));
  } catch (e) {
    next(e);
  }
});

router.get('/inference', async (req, res, next) => {
  try {
    const data = await getInferenceInfo();
    res.json(success(data));
  } catch (e) {
    next(e);
  }
});

router.patch('/config', async (req, res, next) => {
  try {
    const data = await updateConfig(req.body);
    res.json(success(data));
  } catch (e) {
    next(e);
  }
});

export default router;
