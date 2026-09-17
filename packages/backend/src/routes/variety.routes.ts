import { Router } from 'express';
import { getVarieties, getVariety, createVariety, updateVariety, deleteVariety } from '../services/variety.service.js';
import { success } from '../utils/api-response.js';
import { requireAuth } from '../middleware/auth.middleware.js';

const router = Router();

router.use(requireAuth);

router.get('/', async (req, res, next) => {
  try {
    const data = await getVarieties();
    res.json(success(data));
  } catch (e) {
    next(e);
  }
});

router.get('/:id', async (req, res, next) => {
  try {
    const data = await getVariety(req.params.id);
    res.json(success(data));
  } catch (e) {
    next(e);
  }
});

router.post('/', async (req, res, next) => {
  try {
    const data = await createVariety(req.body);
    res.json(success(data));
  } catch (e) {
    next(e);
  }
});

router.patch('/:id', async (req, res, next) => {
  try {
    const data = await updateVariety(req.params.id, req.body);
    res.json(success(data));
  } catch (e) {
    next(e);
  }
});

router.delete('/:id', async (req, res, next) => {
  try {
    await deleteVariety(req.params.id);
    res.json(success(null, 'Variety deleted'));
  } catch (e) {
    next(e);
  }
});

export default router;
