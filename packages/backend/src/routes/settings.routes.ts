import { Router } from 'express';
import { getSettings, updateSettings, resetSettings } from '../services/settings.service.js';
import { success } from '../utils/api-response.js';
import { requireAuth } from '../middleware/auth.middleware.js';

const router = Router();

router.use(requireAuth);

router.get('/', async (req, res, next) => {
  try {
    const data = await getSettings();
    res.json(success(data));
  } catch (e) {
    next(e);
  }
});

router.put('/', async (req, res, next) => {
  try {
    const data = await updateSettings(req.body);
    res.json(success(data));
  } catch (e) {
    next(e);
  }
});

router.patch('/', async (req, res, next) => {
  try {
    const data = await updateSettings(req.body);
    res.json(success(data));
  } catch (e) {
    next(e);
  }
});

router.post('/reset', async (req, res, next) => {
  try {
    const data = await resetSettings();
    res.json(success(data));
  } catch (e) {
    next(e);
  }
});

export default router;
