import { Router } from 'express';
import { createSession, getSessions, getSession, updateSession, deleteSession, updateStatus } from '../services/detection.service.js';
import { success } from '../utils/api-response.js';
import { requireAuth } from '../middleware/auth.middleware.js';

const router = Router();

router.use(requireAuth);

router.post('/', async (req, res, next) => {
  try {
    const data = await createSession(req.body);
    res.json(success(data));
  } catch (e) {
    next(e);
  }
});

router.get('/', async (req, res, next) => {
  try {
    const data = await getSessions();
    res.json(success(data));
  } catch (e) {
    next(e);
  }
});

router.get('/:id', async (req, res, next) => {
  try {
    const data = await getSession(req.params.id);
    res.json(success(data));
  } catch (e) {
    next(e);
  }
});

router.patch('/:id', async (req, res, next) => {
  try {
    const data = await updateSession(req.params.id, req.body);
    res.json(success(data));
  } catch (e) {
    next(e);
  }
});

router.delete('/:id', async (req, res, next) => {
  try {
    await deleteSession(req.params.id);
    res.json(success(null, 'Session deleted'));
  } catch (e) {
    next(e);
  }
});

router.post('/:id/start', async (req, res, next) => {
  try {
    const data = await updateStatus(req.params.id, 'running');
    res.json(success(data));
  } catch (e) {
    next(e);
  }
});

router.post('/:id/stop', async (req, res, next) => {
  try {
    const data = await updateStatus(req.params.id, 'completed');
    res.json(success(data));
  } catch (e) {
    next(e);
  }
});

router.post('/:id/pause', async (req, res, next) => {
  try {
    const data = await updateStatus(req.params.id, 'paused');
    res.json(success(data));
  } catch (e) {
    next(e);
  }
});

export default router;
